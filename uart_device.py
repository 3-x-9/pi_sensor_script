from bluezero import device, async_tools
import random, struct

from database import DatabaseManager

class UARTDevice:
    tx_obj = None
    connected = {} # device : true/false

    db = DatabaseManager()

    @classmethod
    def on_connect(cls, ble_device: device.Device):
        print("Connected to " + str(ble_device.address))
        cls.connected[ble_device.address] = True

    @classmethod
    def on_disconnect(cls, adapter_address, device_address):
        print("Disconnected from " + device_address)
        cls.connected[device_address] = False
        cls.tx_obj = None

    @classmethod
    def uart_notify(cls, notifying, characteristic):
        if notifying:
            print("Client subscribed to notifications")
            cls.tx_obj = characteristic
            async_tools.add_timer_seconds(1, cls.send_mock_ph)
        else:
            print("Client unsubscribed")
            cls.tx_obj = None

    @classmethod
    def send_mock_ph(cls):
        """Called periodically by async_tools"""
        if not cls.tx_obj or not cls.tx_obj.is_notifying:
            # stop timer
            return False

        ph_val = random.uniform(6.5, 7.5)
        byte_list = list(struct.pack("<f", ph_val))
        cls.tx_obj.set_value(byte_list)

        for addr, is_connected in cls.connected.items():
            if is_connected:
                cls.db.save_locally(addr, ph_val)

        print(f"Sent mock PH: {ph_val:.2f}, bytes: {byte_list}")
        return True  # repeat timer

    @classmethod
    def uart_write(cls, value, options):
        print('Received write:', value)
        try:
            print('Text value:', bytes(value).decode('utf-8'))
        except UnicodeDecodeError:
            print("Received non-text data:", value)

    @classmethod
    def uart_read(cls):
        ph_val = random.uniform(6.5, 7.5)
        byte_list = list(struct.pack("<f", ph_val))
        print(f"Read request → {byte_list} = {ph_val:.2f}")
        return byte_list

    def uart_read_db(cls):
        data_list = []
        for id, sensorId, phvalue, created_at, synced in db.get_unsynced:
            data = {
                "sensorId": sensorId,
                "phvalue": phvalue,
                "createdat": created_at 
            }
            payload = json.dumps(data)
            data_list.append(payload)