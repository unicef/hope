from pathlib import Path
from typing import Any, Dict

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand, CommandParser


class Command(BaseCommand):
    requires_migrations_checks = False

    def add_arguments(self, parser: CommandParser) -> None:
        subparsers = parser.add_subparsers(title="command", dest="command", required=True)
        CommandParser(add_help=False)
        test = subparsers.add_parser("test")
        test.add_argument("filename")
        test.add_argument("--target")

        execute = subparsers.add_parser("execute")
        execute.add_argument("id")
        execute.add_argument(
            "--persist",
            action="store_true",
            default=False,
        )

        run = subparsers.add_parser("run")
        run.add_argument("id")
        run.add_argument(
            "--persist",
            action="store_true",
            default=False,
        )
        run.add_argument(
            "--arguments",
            "-a",
            action="store",
            nargs="+",
            default=[],
        )

        subparsers.add_parser("list")

    def _list(self, *args: Any, **options: Any) -> None:
        from hct_mis_api.apps.power_query.models import Query as PowerQuery

        for q in PowerQuery.objects.all():
            self.stdout.write(f"#{q.id:>5}   {q.name[:30]:<32} {q.last_run}")

    def _test(self, *args: Any, **options: Any) -> None:
        from hct_mis_api.apps.power_query.models import Query as PowerQuery

        code = Path(options["filename"]).read_text()
        target = options["target"]
        model = ContentType.objects.get_for_model(apps.get_model(target))
        pq = PowerQuery(name="Test", target=model, code=code)
        arguments = {}
        result, info = pq.run(persist=False, arguments=arguments)
        for entry in result:
            print(type(entry), entry)

    def _run(self, *args: Any, **options: Any) -> None:
        from hct_mis_api.apps.power_query.models import Query as PowerQuery

        query_args: Dict[str, str] = {}
        try:
            for a in options["arguments"]:
                k, v = a.split("=")
                query_args[k] = v
            pq = PowerQuery.objects.get(pk=options["id"])
            result, info = pq.run(persist=options["persist"], arguments=query_args)
            for k, v in info.items():
                self.stdout.write(f"{k}: {v}")
            self.stdout.write("=" * 80)
            for entry in result:
                self.stdout.write(str(entry))
        except Exception as e:
            self.stdout.write(f"Error: {e.__class__.__name__}")
            self.stdout.write(str(e))

    def _execute(self, *args: Any, **options: Any) -> None:
        from hct_mis_api.apps.power_query.models import Query as PowerQuery

        try:
            pq = PowerQuery.objects.get(pk=options["id"])
            result = pq.execute_matrix(persist=options["persist"])
            for entry in result:
                self.stdout.write(str(entry))
        except Exception as e:
            self.stdout.write(f"Error: {e.__class__.__name__}")
            self.stdout.write(str(e))
            raise

    def handle(self, *args: Any, **options: Any) -> None:
        if options["command"] == "list":
            self._list(*args, **options)
        elif options["command"] == "execute":
            self._execute(*args, **options)
        elif options["command"] == "test":
            self._test(*args, **options)
        elif options["command"] == "run":
            self._run(*args, **options)
