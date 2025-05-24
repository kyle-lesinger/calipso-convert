import sys
from pathlib import Path
import click
from .converter import h4_to_h5

@click.command()
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False))
def main(input_file):
    in_path = Path(input_file)
    out_path = in_path.with_suffix(".h5")
    click.echo(f"Converting {in_path} → {out_path}…")
    h4_to_h5(in_path, out_path)
    click.echo("Done!")
    # you can chain here your other steps or just exit
    sys.exit(0)

