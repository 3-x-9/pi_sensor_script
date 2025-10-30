from gi.repository import GLib

# Bluezero modules
from bluezero import adapter
from bluezero import peripheral
from bluezero import device

import random

# constants
UART_SERVICE = "b197db85-f1d2-4023-a9f1-ceda630dd39b"
PHREAD_CHARACTERISTIC = "70ceca29-8ff7-49af-8896-790d7bb30967"
DEVWRITE_CHARACTERISTIC = "8a1f9b2e-1234-5678-9abc-def012345678"


class UARTDevice:
    tx_obj = None

    @classmethod
    def on_connect(cls, ble_device: device.Device):
        print("Connected to " + str(ble_device.address))

    @classmethod
    def on_disconnect(cls, adapter_address, device_address):
        print("Disconnected from " + device_address)

    @classmethod
    def uart_notify(cls, notifying, characteristic):
        if notifying:
            cls.tx_obj = characteristic
            print("client subscribed to notifications")
        else:
            cls.tx_obj = None
            print("client unsubscribed")

    @classmethod
    def update_tx(cls, value):
        if cls.tx_obj:
            print("Sending")
            cls.tx_obj.set_value(value)
        else:
            print("No client connected cant send data")

    @classmethod
    def uart_write(cls, value, options):
        print('raw bytes:', value)
        print('With options:', options)
        try: 
            print('Text value:', bytes(value).decode('utf-8'))
            cls.update_tx(value)
        except UnicodeDecodeError:
            print("recieved non-text data: ", value) 

    @classmethod
    def uart_read(cls):
        ph_val = random.uniform(6.5, 7.5)
        byte_list = [ord(c) for c in f"{ph_val:.2f}"]
        return byte_list


def send_mock_ph():
    if UARTDevice.tx_obj:
        ph_val = random.uniform(6.5, 7.5)
        byte_list = [ord(c) for c in f"{ph_val:.2f}"]
        UARTDevice.tx_obj.set_value(byte_list)
        print("Sent:", ph_val)
    return True  # return True to repeat with GLib


def main(adapter_address):
    print(adapter_address)
    ble_uart = peripheral.Peripheral(adapter_address, local_name='BLE UART')
    ble_uart.add_service(srv_id=1, uuid=UART_SERVICE, primary=True)
    ble_uart.add_characteristic(srv_id=1, chr_id=1, uuid=PHREAD_CHARACTERISTIC,
                                value=[], notifying=False,
                                flags=['notify', 'read'],
                                write_callback=None,
                                read_callback=UARTDevice.uart_read,
                                notify_callback=UARTDevice.uart_notify
                                )
    ble_uart.add_characteristic(srv_id=1, chr_id=2, uuid=DEVWRITE_CHARACTERISTIC,
                                value=[], notifying=False,
                                flags=['write', "write-without-response"],
                                notify_callback=None,
                                read_callback=None,
                                write_callback=UARTDevice.uart_write)

    ble_uart.on_connect = UARTDevice.on_connect
    ble_uart.on_disconnect = UARTDevice.on_disconnect

    ble_uart.publish()


if __name__ == '__main__':
    main(list(adapter.Adapter.available())[0].address)
    GLib.timeout_add_seconds(1, send_mock_ph)
    GLib.MainLoop().run()
