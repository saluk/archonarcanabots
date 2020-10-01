# import time
from locust import HttpUser, task, between


class APIUSer(HttpUser):
    wait_time = between(1, 2)

    @task
    def first10decks(self):
        self.client.get("/decks?start=0&end=10")

    # @task(3)
    # def view_item(self):
    #     for item_id in range(10):
    #         self.client.get(f"/item?id={item_id}", name="/item")
    #         time.sleep(1)

    # def on_start(self):
    #     self.client.post("/login", json={"username":"foo", "password":"bar"})