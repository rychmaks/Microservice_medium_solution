import json
import os

import yaml
from dateutil.parser import parse as dtparse

from service_api.models import models
from service_api.services.database import get_engine, release_engines


class FixtureLoader:

    def __init__(self, client_names, fixture_file_name, host=None):
        self.client_names = client_names
        self.fixture_file_name = fixture_file_name
        self.host = host

    @property
    def file_name(self):
        return os.path.join(os.path.join(os.path.dirname(__file__), "files"), self.fixture_file_name)

    def dict_from_fixture_file(self):
        name, extension = os.path.splitext(self.file_name)
        if extension in [".json", ".js"]:
            return self._dict_from_json_file(self.file_name)

        if extension in [".yaml", ".yml"]:
            return self._dict_from_yaml_file(self.file_name)

        raise Exception("extension must be .js[on], .y[a]ml")

    async def load_data(self):
        data = self.dict_from_fixture_file() or {}
        sample_data = data.get("dataload", {})
        for client_name in self.client_names:
            engine = await get_engine(client=client_name, host=self.host)
            async with engine.acquire() as conn:
                async with conn.begin():
                    for model in models:
                        records = sample_data.get(model.name, [])
                        await self._load_data(conn, model, records)
        await release_engines()

    @staticmethod
    async def _load_data(conn, table, records):
        for record in records:
            await conn.execute(table.insert().values(**record))

    @staticmethod
    def _dict_from_json_file(filename):

        def _datetime_parser(dct):
            for key, value in dct.items():
                try:
                    dct[key] = dtparse(value)
                except Exception:
                    pass
            return dct

        with open(filename) as fin:
            return json.load(fin, object_hook=_datetime_parser)

    @staticmethod
    def _dict_from_yaml_file(filename):
        with open(filename) as fin:
            return yaml.load(fin)
