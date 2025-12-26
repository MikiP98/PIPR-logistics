from logistics.database.database import Database
from logistics.io_utils import ask_for_bool, ask_for_float, ask_for_time, warn
from logistics.pipeline_loops.virtual_clock import VirtualClock


def change_time_simulation_scale_task(_: Database, clock: VirtualClock) -> None:
    scale = ask_for_float("Provide the scale of the time simulation")
    confirm = ask_for_bool(f"Confirm the change of the time simulation from '{clock.get_scale()}' to '{scale}'")
    if confirm:
        clock.set_scale(scale)
    else:
        print()
        warn("Cancelling the change of the time simulation scale")


def offset_simulation_time_task(_: Database, clock: VirtualClock) -> None:
    weeks, days, hours, minutes, seconds = ask_for_time("Provide the offset of the time simulation")
    confirm = ask_for_bool(
        "Confirm the offset of the time simulation by "
        f"{weeks:01}:{days:02}:{hours:02}:{minutes:02}:{seconds:02} "
        f"({(((weeks * 7 + days) * 24 + hours) * 60 + minutes) * 60 + seconds} seconds)"
    )
    if confirm:
        clock.jump((hours * 60 + minutes) * 60 + seconds)
    else:
        print()
        warn("Cancelling the offset of the time simulation")
