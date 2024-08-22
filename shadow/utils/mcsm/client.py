from typing import Literal

from yarl import URL
from httpx import AsyncClient


class PanelApp:
    def __init__(self, url: str, key: str):
        self.url = URL(url)
        self.key = key

    async def api_overview(self) -> dict:
        async with AsyncClient() as client:
            resp = await client.get(str(self.url / "api/overview"), params={"apikey": self.key})
            return resp.json()

    async def api_auth_search(self, user_name: str | None, page: int, page_size: int, role: str | None) -> dict:
        if user_name is None:
            user_name = ""
        if role is None:
            role = ""
        async with AsyncClient() as client:
            resp = await client.get(
                str(self.url / "api/auth/search"),
                params={"apikey": self.key, "userName": user_name, "page": page, "page_size": page_size, "role": role},
            )
            return resp.json()

    async def api_auth_create(self, username: str, password: str, permission: int) -> dict:
        """创建用户"""
        async with AsyncClient() as client:
            resp = await client.post(
                str(self.url / "api/auth"),
                params={"apikey": self.key},
                json={"username": username, "password": password, "permission": permission},
            )
            return resp.json()

    async def api_auth_update(self, uuid: str, config: dict) -> dict:
        async with AsyncClient() as client:
            resp = await client.put(str(self.url / "api/auth" / uuid), params={"apikey": self.key}, json=config)
            return resp.json()

    async def api_service_remote_service_instances(
            self, daemon_id: str, page: int, page_size: int, status: str, instance_name: str | None = None
    ) -> dict:
        async with AsyncClient() as client:
            resp = await client.get(
                str(self.url / "api/service/remote_service_instances"),
                params={
                    "apikey": self.key,
                    "daemonId": daemon_id,
                    "page": page,
                    "page_size": page_size,
                    "status": status,
                    "instance_name": instance_name,
                },
            )
            return resp.json()

    async def api_instance(self, uuid: str, daemon_id: str) -> dict:
        async with AsyncClient() as client:
            resp = await client.get(
                str(self.url / "api/instance"), params={"apikey": self.key, "daemonId": daemon_id, "uuid": uuid}
            )
            return resp.json()

    async def api_instance_create(self, daemon_id: str, config: dict) -> dict:
        async with AsyncClient() as client:
            resp = await client.post(
                str(self.url / "api/instance"), params={"apikey": self.key, "daemonId": daemon_id}, json=config
            )
            return resp.json()

    async def api_instance_update(self, uuid: str, daemon_id: str, config: dict) -> dict:
        async with AsyncClient() as client:
            resp = await client.put(
                str(self.url / "api/instance" / uuid), params={"apikey": self.key, "daemonId": daemon_id}, json=config
            )
            return resp.json()

    async def api_instance_delete(self, daemon_id: str, uuids: list[str], delete_file: bool) -> dict:
        async with AsyncClient() as client:
            resp = await client.request(
                "DELETE",
                str(self.url / "api/instance"),
                params={"apikey": self.key, "daemonId": daemon_id},
                json={"uuids": uuids, "deleteFile": delete_file},
            )
            return resp.json()

    async def api_protected_instance_open(self, uuid: str, daemon_id: str) -> dict:
        async with AsyncClient() as client:
            resp = await client.get(
                str(self.url / "api/protected_instance/open"),
                params={"apikey": self.key, "daemonId": daemon_id, "uuid": uuid},
            )
            return resp.json()

    async def api_protected_instance_stop(self, uuid: str, daemon_id: str) -> dict:
        async with AsyncClient() as client:
            resp = await client.get(
                str(self.url / "api/protected_instance/stop"),
                params={"apikey": self.key, "daemonId": daemon_id, "uuid": uuid},
            )
            return resp.json()

    async def api_protected_instance_restart(self, uuid: str, daemon_id: str) -> dict:
        async with AsyncClient() as client:
            resp = await client.get(
                str(self.url / "api/protected_instance/restart"),
                params={"apikey": self.key, "daemonId": daemon_id, "uuid": uuid},
            )
            return resp.json()

    async def api_protected_instance_kill(self, uuid: str, daemon_id: str) -> dict:
        async with AsyncClient() as client:
            resp = await client.get(
                str(self.url / "api/protected_instance/kill"),
                params={"apikey": self.key, "daemonId": daemon_id, "uuid": uuid},
            )
            return resp.json()

    async def api_instance_multi_action(
            self, action: Literal["start", "stop", "restart", "kill"], data: list[dict[str, str]]
    ) -> dict:
        """
        批量操作
        :param action: start, stop, restart, kill
        :param data: { instanceUuid: string, daemonId: string }[]
        :return: { "status": 200, "data": true, "time": 1718594177859 }
        """
        async with AsyncClient() as client:
            resp = await client.post(
                str(self.url / f"api/instance/multi_{action}"),
                params={"apikey": self.key},
                json=data,
            )
            return resp.json()

    async def api_protected_instance_asynchronous(self, uuid: str, daemon_id: str) -> dict:
        """更新命令"""
        async with AsyncClient() as client:
            resp = await client.get(
                str(self.url / "api/protected_instance/asynchronous"),
                params={"apikey": self.key, "daemonId": daemon_id, "uuid": uuid, "task_name": "update"},
            )
            return resp.json()

    async def api_protected_instance_command(self, uuid: str, daemon_id: str, command: str) -> dict:
        """执行命令"""
        async with AsyncClient() as client:
            resp = await client.get(
                str(self.url / "api/protected_instance/command"),
                params={"apikey": self.key, "daemonId": daemon_id, "uuid": uuid, "command": command},
            )
            return resp.json()

    async def api_protected_instance_outputlog(self, uuid: str, daemon_id: str, size: int | None = None) -> dict:
        """size单位应该是字节"""
        if size is None:
            size = ""
        async with AsyncClient() as client:
            resp = await client.get(
                str(self.url / "api/protected_instance/outputlog"),
                params={"apikey": self.key, "daemonId": daemon_id, "uuid": uuid, "size": size},
            )
            return resp.json()

    async def api_protected_instance_install_instance(
            self, uuid: str, daemon_id: str, target_url: str, title: str, description: str
    ) -> dict:
        async with AsyncClient() as client:
            resp = await client.post(
                str(self.url / "api/protected_instance/install_instance"),
                params={
                    "apikey": self.key,
                    "daemonId": daemon_id,
                    "uuid": uuid,
                },
                json={
                    "targetUrl": target_url,
                    "title": title,
                    "description": description,
                },
            )
            return resp.json()
