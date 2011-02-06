"""
    clover.roulette
    ~~~~~~~~~~~~~~~

    Generate color schemes from COLOURlovers palettes.
"""
from random import choice
from commons.core.structures import simple_enum
from commons.core.graphics.color import HTML4_COLORS, render_template, \
                                        Color, PaletteAggregate
import clover


__version__ = "0.0.1"


DEFAULT_FILTERS = [
    #: Ignore colors with extreme variations in saturation.
    lambda color, palette:
        abs(palette.average_saturation - color.saturation) <= 50,
    #: Ignore extremely bright colors.
    lambda color, palette:
        color.saturation > 90 and color.value > 90
]


class Roulette(PaletteAggregate):
    """
    Generate a palette containing colors within a minimum distance from those
    of the target palette.
    """

    REDUCTION_METHODS = simple_enum("RANDOM", "MIN_DISTANCE", "MAX_DISTANCE")

    def __init__(self, target=HTML4_COLORS, filters=DEFAULT_FILTERS,
                 palettes=[], randomize=True, max_palettes=10):
        """
        :param palettes: An optional list of :class:`clover.Palette` objects.
        :param randomize: If *True*, pulls in random COLOURlovers palettes
                          until either the aggregate is complete or the
                          maximum number of palettes allowed to be requested
                          is reached.
        :param max_palettes: Specifies how many palettes may be requested
                             before aborting.
        """
        super(Roulette, self).__init__(target, filters)
        self.max_palettes = max_palettes
        self.randomize = randomize
        map(self.add_palette, palettes)

    def run(self, reduce_palette=True):
        """Attempts to fill this :class:`PaletteAggregate`."""
        while not self.complete:
            self.randomize and self.add_palette(clover.Palette.from_random())
            if len(self.palettes) == self.max_palettes: break
        if not self.complete:
            self.fill_missing_colors()
            reduce_palette and self.reduce_palette()

    def fill_missing_colors(self):
        """
        Generates any missing colors based on average saturation and value,
        and the sum and difference of the default hue and average hue
        difference (between adjacent colors).
        """
        assert len(self) > 2, "Need at least 2 colors in palette to continue"
        hue_diff = self.get_average_difference("hue")
        avg_saturation, avg_value = map(
            self.get_average_value,
            ("saturation", "value"))
        colors = sorted(self.target.items(), key=lambda (name, rgb): rgb)
        for index in range(len(colors)):
            name, rgb = colors[index]
            if name in self: continue

            default_color = Color(*rgb)
            candidates = []
            if (default_color.hue - hue_diff) >= 0:
                candidates.append(Color.from_hsv([
                    default_color.hue - hue_diff,
                    avg_saturation,
                    avg_value]))
            if (default_color.hue + hue_diff) <= 255:
                candidates.append(Color.from_hsv([
                    default_color.hue + hue_diff,
                    avg_saturation,
                    avg_value]))

            self[name] = map(
                lambda candidate:
                    (candidate, default_color.distance(candidate)),
                candidates)

    def reduce_palette(self, method=REDUCTION_METHODS.MIN_DISTANCE):
        """
        Reduce multiple colors assigned to target names in a palette to
        a single color.
        """
        for name, colors in self.sorted.items():
            if len(colors) == 1:
                self[name] = colors[0][0]
                continue
            if method == self.REDUCTION_METHODS.RANDOM:
                self[name] = choice(colors)[0]
            elif method == self.REDUCTION_METHODS.MIN_DISTANCE:
                self[name] = colors[0][0]
            elif method == self.REDUCTION_METHODS.MAX_DISTANCE:
                self[name] = colors[-1][0]
