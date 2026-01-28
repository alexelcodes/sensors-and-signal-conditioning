#include <stdio.h>
#include <string.h> // for memcpy
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_rom_sys.h"       // for esp_rom_delay_us (short delays)
#include "driver/i2c_master.h" // new I2C driver API
#include "bme68x.h"

#define I2C_PORT I2C_NUM_0
#define SDA_PIN 2
#define SCL_PIN 3
#define SENSOR_ADDR 0x77
#define I2C_FREQ 100000
#define TIMEOUT_MS 50

// --- Bridge between Bosch driver and ESP-IDF I2C API ---
static i2c_master_dev_handle_t g_dev; // global I2C device handle

// I2C read function for Bosch driver
static int8_t bme_user_read(uint8_t reg_addr, uint8_t *reg_data, uint32_t len, void *intf_ptr)
{
    (void)intf_ptr;
    esp_err_t e = i2c_master_transmit_receive(g_dev, &reg_addr, 1, reg_data, len, TIMEOUT_MS);
    return (e == ESP_OK) ? 0 : -1;
}

// I2C write function for Bosch driver
static int8_t bme_user_write(uint8_t reg_addr, const uint8_t *reg_data, uint32_t len, void *intf_ptr)
{
    (void)intf_ptr;
    uint8_t buf[1 + 32];
    if (len > 32)
        return -1; // simple protection
    buf[0] = reg_addr;
    memcpy(&buf[1], reg_data, len);
    esp_err_t e = i2c_master_transmit(g_dev, buf, 1 + len, TIMEOUT_MS);
    return (e == ESP_OK) ? 0 : -1;
}

// Delay function for Bosch driver
static void bme_user_delay_us(uint32_t us, void *intf_ptr)
{
    (void)intf_ptr;
    if (us >= 1000)
        vTaskDelay(pdMS_TO_TICKS((us + 999) / 1000)); // use FreeRTOS delay for long waits
    else
        esp_rom_delay_us(us); // short busy-wait delay
}

void app_main(void)
{
    // 1) Initialize I2C bus
    i2c_master_bus_handle_t bus = NULL;
    i2c_master_bus_config_t bus_cfg = {
        .i2c_port = I2C_PORT,
        .sda_io_num = SDA_PIN,
        .scl_io_num = SCL_PIN,
        .clk_source = I2C_CLK_SRC_DEFAULT,
        .glitch_ignore_cnt = 7,
        .flags = {.enable_internal_pullup = true},
    };
    if (i2c_new_master_bus(&bus_cfg, &bus) != ESP_OK)
    {
        printf("I2C bus init failed\n");
        return;
    }

    // 2) Register I2C device (BME688)
    i2c_device_config_t dev_cfg = {
        .device_address = SENSOR_ADDR,
        .scl_speed_hz = I2C_FREQ,
        .flags = {.disable_ack_check = false},
    };
    if (i2c_master_bus_add_device(bus, &dev_cfg, &g_dev) != ESP_OK)
    {
        printf("Add device failed\n");
        return;
    }

    // 3) Quick check – read CHIP_ID register
    uint8_t who = 0xD0, id = 0;
    i2c_master_transmit_receive(g_dev, &who, 1, &id, 1, TIMEOUT_MS);
    printf("CHIP_ID = 0x%02X\n", id); // expected 0x61

    // 4) Initialize Bosch driver
    struct bme68x_dev dev = {0};
    dev.intf = BME68X_I2C_INTF;
    dev.read = bme_user_read;
    dev.write = bme_user_write;
    dev.delay_us = bme_user_delay_us;
    dev.intf_ptr = NULL; // not used (global g_dev instead)

    if (bme68x_init(&dev) != BME68X_OK)
    {
        printf("bme68x_init failed\n");
        return;
    }

    // 5) Basic oversampling and filter setup
    struct bme68x_conf conf = {0};
    conf.os_hum = BME68X_OS_2X;
    conf.os_pres = BME68X_OS_4X;
    conf.os_temp = BME68X_OS_8X;
    conf.filter = BME68X_FILTER_OFF;
    bme68x_set_conf(&conf, &dev);

    // 6) Enable gas sensor heater
    struct bme68x_heatr_conf heat = {0};
    heat.enable = BME68X_ENABLE;
    heat.heatr_temp = 320; // °C
    heat.heatr_dur = 150;  // ms
    bme68x_set_heatr_conf(BME68X_FORCED_MODE, &heat, &dev);

    // 7) Get measurement duration for timing
    uint32_t meas_us = bme68x_get_meas_dur(BME68X_FORCED_MODE, &conf, &dev);

    // CSV header
    printf("timestamp_ms;temperature_C;humidity_pct;pressure_hPa;gas_ohm\n");

    // 8) Continuous measurement loop
    int warmup_samples = 1; // number of first valid samples to skip

    while (1)
    {
        // Trigger one forced measurement
        bme68x_set_op_mode(BME68X_FORCED_MODE, &dev);
        dev.delay_us(meas_us + (uint32_t)heat.heatr_dur * 1000U, dev.intf_ptr);

        // Read data
        struct bme68x_data data[3];
        uint8_t n = 0;
        if (bme68x_get_data(BME68X_FORCED_MODE, data, &n, &dev) == BME68X_OK && n > 0)
        {
            if (warmup_samples > 0)
            {
                // Skip first N samples after boot
                warmup_samples--;
            }
            else
            {
                printf("%lu;%.3f;%.2f;%.2f;%.0f\n",
                       (unsigned long)(xTaskGetTickCount() * portTICK_PERIOD_MS),
                       data[0].temperature,
                       data[0].humidity,
                       data[0].pressure / 100.0f,
                       data[0].gas_resistance);
            }
        }

        // Wait 2 seconds between measurements
        vTaskDelay(pdMS_TO_TICKS(2000));
    }
}