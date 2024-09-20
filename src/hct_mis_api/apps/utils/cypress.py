import os
from typing import Dict

from django.conf import settings
from django.core.management import call_command
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt


def cypress_post(data: Dict) -> HttpResponse:
    command = data.get("command")
    print(f"Handling cy command: {data}")

    if not command:
        return HttpResponse("No command provided", status=400)

    if command == "init-e2e-scenario":
        scenario = data.get("scenario")
        if not scenario:
            return HttpResponse("No scenario provided", status=400)
        seed = data.get("seed")
        if not seed:
            return HttpResponse("No seed provided", status=400)
        call_command(command, scenario, "--seed", seed)

    elif command == "generate-xlsx-files":
        household_size = data.get("size")
        if not household_size:
            return HttpResponse("No household size provided", status=400)
        seed = data.get("seed")
        if not seed:
            return HttpResponse("No seed provided", status=400)
        print(f"Generating xlsx files for household size {household_size} with seed {seed}")
        call_command("generate_rdi_xlsx_files", household_size, "--seed", seed)

    raise ValueError(f"Unknown command: {command}")


@csrf_exempt
def handle_cypress_command(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        cypress_post(request.POST)
        return HttpResponse("OK", status=200)
    return HttpResponse("Method not allowed", status=405)


@csrf_exempt
def get_cypress_xlsx_file(request: HttpRequest, seed: int) -> HttpResponse:
    if request.method != "GET":
        return HttpResponse("Method not allowed", status=405)

    generated_dir = os.path.join(settings.PROJECT_ROOT, "..", "generated")
    for filename in os.listdir(generated_dir):
        if str(seed) in filename:
            filepath = os.path.join(generated_dir, filename)
            with open(filepath, "rb") as f:
                response = HttpResponse(
                    f.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                response["Content-Disposition"] = f"attachment; filename={filename}"
                return response

    return HttpResponse("File not found", status=404)
