from bluezero import adapter, peripheral
from uart_device import UARTDevice

# UUIDs
UART_SERVICE = "b197db85-f1d2-4023-a9f1-ceda630dd39b"
PHREAD_CHARACTERISTIC = "70ceca29-8ff7-49af-8896-790d7bb30967"
DEVWRITE_CHARACTERISTIC = "8a1f9b2e-1234-5678-9abc-def012345678"


def main(adapter_address):
    print("Using adapter:", adapter_address)

    ble_uart = peripheral.Peripheral(adapter_address, local_name='BLE UART')
    ble_uart.add_service(srv_id=1, uuid=UART_SERVICE, primary=True)

    # PH Read characteristic
    ble_uart.add_characteristic(
        srv_id=1, chr_id=1, uuid=PHREAD_CHARACTERISTIC,
        value=[], notifying=False,
        flags=['notify', 'read'],
        read_callback=UARTDevice.uart_read,
        notify_callback=UARTDevice.uart_notify
    )

    # Write characteristic
    ble_uart.add_characteristic(
        srv_id=1, chr_id=2, uuid=DEVWRITE_CHARACTERISTIC,
        value=[], notifying=False,
        flags=['write', 'write-without-response'],
        write_callback=UARTDevice.uart_write
    )

    ble_uart.on_connect = UARTDevice.on_connect
    ble_uart.on_disconnect = UARTDevice.on_disconnect

    ble_uart.publish()


if __name__ == '__main__':
    main(list(adapter.Adapter.available())[0].address)
