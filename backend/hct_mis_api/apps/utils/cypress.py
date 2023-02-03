from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command


@csrf_exempt
def handle_cypress_command(request):
    data = request.POST
    print(f"Handling cy command: {data}")
    command = data.get("command")

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

    return HttpResponse("OK", status=200)
