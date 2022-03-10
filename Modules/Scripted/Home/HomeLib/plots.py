import slicer, qt
from .constants import *


def createPlotView():
  """Create and return a qMRMLPlotView widget.
  It is associated to the main scene, and it also gets a button for fitToContent."""
  plot_view = slicer.qMRMLPlotView()
  plot_view.setMRMLScene(slicer.mrmlScene)

  fit_plot_tool_button = qt.QToolButton()
  fit_plot_tool_button.clicked.connect(lambda: plot_view.fitToContent())

  # Put the QToolButton in the top right corner of the plot
  assert(plot_view.layout() is None) # failure here indicates a slicer change in which plot views gained layouts, which we should take care not to replace
  plot_view.setLayout(qt.QHBoxLayout())
  plot_view.layout().insertWidget(1,fit_plot_tool_button,0,qt.Qt.AlignTop)
  spacer = qt.QSpacerItem(20,20,qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)
  plot_view.layout().insertItem(0,spacer)
  plot_view.layout().margin=0

  # Give it a nice appearance
  fit_plot_tool_button.setIconSize(qt.QSize(10,10))
  fit_plot_tool_button.setIcon(qt.QIcon(":Icons/SlicesFitToWindow.png"))
  fit_plot_tool_button.setStyleSheet(f"background-color:#{BAR_WIDGET_COLOR};")
  fit_plot_tool_button.setAutoRaise(True)

  fit_plot_tool_button.setToolTip("Reset zoom to fit entire plot")

  return plot_view


class SlicerPlotData:
  """Container for and manager of the nodes associated to a slicer plot view."""

  # A plot view node we will keep empty in order to have a way of displaying no plot
  empty_plot_view_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotViewNode", "SlicerPlotDataEmptyPlotViewNode")

  def __init__(self, name:str):
    """Create SlicerPlotData, making a qMRMLPlotView and a vtkMRMLPlotViewNode with the given name."""
    self.name = name
    self.plot_view = createPlotView()
    self.plot_view_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotViewNode", name+"PlotView")
    self.plot_view.setMRMLPlotViewNode(self.plot_view_node)
    self.plot_nodes = {} # chart, table, and series; see the parameter "nodes" in the doc of slicer.util.plot


  def set_plot_data(self, data, x_axis_label:str, y_axis_label:str, title=None, legend_label=None):
    """
    Populate the plot with the data from the given numpy array.

    Args:
      data: A numpy array of shape (N,2) containing the data to plot
      x_axis_label: the title of the x axis to display
      y_axis_label: the title of the y axis to display
      title: plot title
      legend_label: the text to put in the legend
    """

    if title is None: title = self.name
    if legend_label is None: legend_label = title

    if len(data.shape)!=2 or data.shape[1]!=2:
      raise ValueError(f"data was expected to be a numpy array of shape (N,2), got {tuple(data.shape)}")

    # To solve github.com/KitwareMedical/lungair-desktop-application/issues/27
    # we avoid changing plots while they are associated to a plot view.
    self.plot_view.setMRMLPlotViewNode(self.empty_plot_view_node)

    plot_chart_node = slicer.util.plot(
      data, 0, show = False,
      title = title,
      columnNames = [x_axis_label, y_axis_label],
      nodes = self.plot_nodes
    )
    plot_chart_node.SetXAxisTitle(x_axis_label)
    plot_chart_node.SetYAxisTitle(y_axis_label)
    assert(len(self.plot_nodes["series"]) == 1)
    self.plot_nodes["series"][0].SetName(legend_label) # This text is displayed in the legend
    self.plot_view_node.SetPlotChartNodeID(plot_chart_node.GetID())

    self.plot_view.setMRMLPlotViewNode(self.plot_view_node)