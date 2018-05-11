from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from math import fabs

from compas.plotters.core import draw_xpoints_xy
from compas.plotters.core import draw_xlines_xy
from compas.plotters.core import draw_xarrows_xy
from compas.plotters.core import draw_xlabels_xy

from compas.utilities import color_to_colordict
from compas.utilities import is_color_light

from compas.plotters.core import size_to_sizedict

import matplotlib.pyplot as plt


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2014 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = [
    'Viewer'
]


class Viewer(object):
    """"""

    def __init__(self, form, force, delay_setup=True):
        self.form  = form
        self.force = force
        self.fig   = None
        self.ax1   = None
        self.ax2   = None

        self.default_facecolor   = '#ffffff'
        self.default_edgecolor   = '#000000'
        self.default_vertexcolor = '#ffffff'
        self.default_vertexsize  = 0.1
        self.default_edgewidth   = 1.0

        self.default_compressioncolor   = '#0000ff'
        self.default_tensioncolor       = '#ff0000'
        self.default_externalforcecolor = '#00ff00'
        self.default_externalforcewidth = 2.0

        self.default_textcolor = '#000000'
        self.default_fontsize  = 8

        self.default_pointsize  = 0.1
        self.default_linewidth  = 1.0
        self.default_pointcolor = '#ffffff'
        self.default_linecolor  = '#000000'
        self.default_linestyle  = '-'

        if not delay_setup:
            self.setup()

    def setup(self):
        self.fig = plt.figure(figsize=(14.4, 9), tight_layout=True)
        self.ax1 = self.fig.add_subplot('121')
        self.ax2 = self.fig.add_subplot('122')
        self.ax1.set_aspect('equal')
        self.ax2.set_aspect('equal')
        self.ax1.set_xticks([])
        self.ax1.set_yticks([])
        self.ax1.set_xmargin(1.0)
        self.ax1.set_ymargin(1.0)
        self.ax1.set_xlim(-1.0, 11.0)
        self.ax1.set_ylim(-1.0, 11.0)
        self.ax2.set_xticks([])
        self.ax2.set_yticks([])
        self.ax2.set_xmargin(1.0)
        self.ax2.set_ymargin(1.0)
        self.ax2.set_xlim(-1.0, 11.0)
        self.ax2.set_ylim(-1.0, 11.0)
        self.fig.patch.set_facecolor('white')
        self.ax1.axis('off')
        self.ax2.axis('off')

    def draw_form(self,
                  vertices_on=True,
                  edges_on=True,
                  faces_on=False,
                  forces_on=True,
                  vertexcolor=None,
                  edgecolor=None,
                  facecolor=None,
                  edgelabel=None,
                  vertexlabel=None,
                  facelabel=None,
                  vertexsize=None,
                  forcescale=1.0,
                  lines=None,
                  points=None):
        """"""
        # preprocess

        vertexlabel = vertexlabel or {}
        edgelabel   = edgelabel or {}
        facelabel   = facelabel or {}
        vertexsize  = size_to_sizedict(vertexsize, self.form.vertices(), self.default_vertexsize)
        vertexcolor = color_to_colordict(vertexcolor, self.form.vertices(), self.default_vertexcolor)
        edgecolor   = color_to_colordict(edgecolor, self.form.edges(), self.default_edgecolor)
        facecolor   = color_to_colordict(facecolor, self.form.faces(), self.default_facecolor)

        # scale and position

        x = self.form.get_vertices_attribute('x')
        y = self.form.get_vertices_attribute('y')

        if lines:
            x += [line['start'][0] for line in lines]
            x += [line['end'][0] for line in lines]
            y += [line['start'][1] for line in lines]
            y += [line['end'][1] for line in lines]

        xmin, ymin = min(x), min(y)
        xmax, ymax = max(x), max(y)
        dx, dy = -xmin, -ymin
        scale  = max(fabs(xmax - xmin) / 10.0, fabs(ymax - ymin) / 10.0)

        # vertices

        if vertices_on:
            _points = []
            for key, attr in self.form.vertices(True):
                bgcolor = vertexcolor[key]
                _points.append({
                    'pos'       : [(attr['x'] + dx) / scale, (attr['y'] + dy) / scale],
                    'radius'    : vertexsize[key],
                    'facecolor' : vertexcolor[key],
                    'edgecolor' : self.default_edgecolor,
                    'linewidth' : self.default_edgewidth * 0.5,
                    'text'      : None if key not in vertexlabel else str(vertexlabel[key]),
                    'textcolor' : '#000000' if is_color_light(bgcolor) else '#ffffff',
                    'fontsize'  : self.default_fontsize,
                })
            draw_xpoints_xy(_points, self.ax1)

        # edges

        if edges_on:
            leaves  = set(self.form.leaves())
            _lines  = []
            _arrows = []
            for u, v, attr in self.form.edges(True):
                sp, ep = self.form.edge_coordinates(u, v, 'xy')
                sp = ((sp[0] + dx) / scale, (sp[1] + dy) / scale)
                ep = ((ep[0] + dx) / scale, (ep[1] + dy) / scale)
                if u in leaves or v in leaves:
                    text  = None if (u, v) not in edgelabel else str(edgelabel[(u, v)])
                    _arrows.append({
                        'start'    : sp,
                        'end'      : ep,
                        'width'    : self.default_externalforcewidth,
                        'color'    : self.default_externalforcecolor,
                        'text'     : text,
                        'fontsize' : self.default_fontsize
                    })
                else:
                    if forces_on:
                        width = forcescale * fabs(attr['f'])
                        color = self.default_tensioncolor if attr['f'] > 0 else self.default_compressioncolor
                        text  = None if (u, v) not in edgelabel else str(edgelabel[(u, v)])
                        _lines.append({
                            'start'    : sp,
                            'end'      : ep,
                            'width'    : width,
                            'color'    : color,
                            'text'     : text,
                            'fontsize' : self.default_fontsize
                        })
                    _arrows.append({
                        'start' : sp,
                        'end'   : ep,
                        'width' : self.default_edgewidth
                    })
            if _arrows:
                draw_xarrows_xy(_arrows, self.ax1)
            if _lines:
                draw_xlines_xy(_lines, self.ax1, alpha=0.5)

        # faces
        # if faces_on:

        _labels = []
        for fkey in facelabel:
            x, y, _ = self.form.face_centroid(fkey)
            _labels.append({
                'pos'      : [(x + dx) / scale, (y + dy) / scale],
                'text'     : str(facelabel[fkey]),
                'fontsize' : self.default_fontsize,
                'color'    : self.default_facecolor,
                'textcolor': self.default_textcolor,
            })
        if _labels:
            draw_xlabels_xy(_labels, self.ax1)

        # points

        if points:
            _points = []
            for point in points:
                x, y, _ = point['pos']
                _points.append({
                    'pos'       : [(x + dx) / scale, (y + dy) / scale],
                    'text'      : point.get('text', ''),
                    'radius'    : point.get('size', self.default_pointsize),
                    'textcolor' : point.get('textcolor', self.default_textcolor),
                    'facecolor' : point.get('facecolor', self.default_pointcolor),
                    'edgecolor' : point.get('edgecolor', self.default_linecolor),
                    'fontsize'  : self.default_fontsize
                })
            draw_xpoints_xy(_points, self.ax1)

        # lines

        if lines:
            _lines = {}
            style = lines[0].get('style', self.default_linestyle)
            for line in lines:
                temp = line.get('style', self.default_linestyle)
                if temp == style:
                    if temp not in _lines:
                        _lines[temp] = []
                else:
                    _lines[temp] = []
                style = temp
                _lines[temp].append({
                    'start'     : [(line['start'][0] + dx) / scale, (line['start'][1] + dy) / scale],
                    'end'       : [(line['end'][0] + dx) / scale, (line['end'][1] + dy) / scale],
                    'width'     : line.get('width', self.default_linewidth),
                    'color'     : line.get('color', self.default_linecolor),
                    'text'      : line.get('text', ''),
                    'textcolor' : line.get('textcolor', self.default_textcolor),
                    'fontsize'  : self.default_fontsize
                })
            for style in _lines:
                draw_xlines_xy(_lines[style], self.ax1, linestyle=style)

    def draw_force(self,
                   vertices_on=True,
                   edges_on=True,
                   faces_on=False,
                   forces_on=True,
                   vertexcolor=None,
                   edgecolor=None,
                   facecolor=None,
                   edgelabel=None,
                   vertexlabel=None,
                   vertexsize=None,
                   lines=None,
                   points=None):
        """"""
        # preprocess

        vertexlabel = vertexlabel or {}
        edgelabel   = edgelabel or {}
        vertexsize  = size_to_sizedict(vertexsize, self.force.vertices(), self.default_vertexsize)
        vertexcolor = color_to_colordict(vertexcolor, self.force.vertices(), self.default_vertexcolor)
        edgecolor   = color_to_colordict(edgecolor, self.force.edges(), self.default_edgecolor)

        # scale and position

        x = self.force.get_vertices_attribute('x')
        y = self.force.get_vertices_attribute('y')
        if lines:
            x += [line['start'][0] for line in lines]
            x += [line['end'][0] for line in lines]
            y += [line['start'][1] for line in lines]
            y += [line['end'][1] for line in lines]
        xmin, ymin = min(x), min(y)
        xmax, ymax = max(x), max(y)
        dx, dy = -xmin, -ymin
        scale  = max(fabs(xmax - xmin) / 10.0, fabs(ymax - ymin) / 10.0)

        # vertices

        if vertices_on:
            _points = []
            for key, attr in self.force.vertices(True):
                bgcolor = vertexcolor[key]
                _points.append({
                    'pos'       : ((attr['x'] + dx) / scale, (attr['y'] + dy) / scale),
                    'radius'    : vertexsize[key],
                    'facecolor' : bgcolor,
                    'edgecolor' : self.default_edgecolor,
                    'linewidth' : self.default_edgewidth * 0.5,
                    'text'      : None if key not in vertexlabel else str(vertexlabel[key]),
                    'textcolor' : '#000000' if is_color_light(bgcolor) else '#ffffff',
                    'fontsize'  : self.default_fontsize
                })
            draw_xpoints_xy(_points, self.ax2)

        # edges

        if edges_on:
            leaves = set(self.form.leaves())
            _arrows = []
            for u, v, attr in self.force.edges(True):
                sp, ep = self.force.edge_coordinates(u, v, 'xy')
                sp = ((sp[0] + dx) / scale, (sp[1] + dy) / scale)
                ep = ((ep[0] + dx) / scale, (ep[1] + dy) / scale)
                form_u, form_v = self.form.face_adjacency_edge(u, v)
                if form_u in leaves or form_v in leaves:
                    _arrows.append({
                        'start' : sp,
                        'end'   : ep,
                        'color' : self.default_externalforcecolor,
                        'width' : self.default_externalforcewidth
                    })
                else:
                    _arrows.append({
                        'start' : sp,
                        'end'   : ep,
                        'color' : self.default_edgecolor,
                        'width' : self.default_edgewidth,
                    })
            draw_xarrows_xy(_arrows, self.ax2)

        # lines

        if lines:
            _lines = {}
            style = lines[0].get('style', self.default_linestyle)
            for line in lines:
                temp = line.get('style', self.default_linestyle)
                if temp == style:
                    if temp not in _lines:
                        _lines[temp] = []
                else:
                    _lines[temp] = []
                style = temp
                _lines[temp].append({
                    'start'     : [(line['start'][0] + dx) / scale, (line['start'][1] + dy) / scale],
                    'end'       : [(line['end'][0] + dx) / scale, (line['end'][1] + dy) / scale],
                    'width'     : line.get('width', self.default_linewidth),
                    'color'     : line.get('color', self.default_linecolor),
                    'text'      : line.get('text', ''),
                    'textcolor' : line.get('textcolor', self.default_textcolor),
                    'fontsize'  : self.default_fontsize
                })
            for style in _lines:
                draw_xlines_xy(_lines[style], self.ax2, linestyle=style)

    def show(self):
        plt.show()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas_ags

    from compas_ags.diagrams import FormDiagram
    from compas_ags.diagrams import ForceDiagram

    form = FormDiagram.from_obj(compas_ags.get('paper/grid_irregular.obj'))
    form.identify_fixed()

    force = ForceDiagram.from_formdiagram(form)

    viewer = Viewer(form, force, delay_setup=False)

    viewer.draw_form(edgelabel={(u, v): '{:.1f}'.format(form.edge_length(u, v)) for u, v in form.edges()})
    viewer.draw_force()

    viewer.show()
