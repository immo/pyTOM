from Tix import Frame, Scrollbar, HORIZONTAL
from MultiSelectTree import MultiSelectTree

class ScrollableMultiSelectTree(Frame):
    def __init__(self, master, root_id, root_label='',
                 get_contents_callback=None, dist_x=15, dist_y=15,
                 text_offset=10, line_flag=1, expanded_icon=None,
                 collapsed_icon=None, regular_icon=None, plus_icon=None,
                 minus_icon=None, unchecked_icon=None, checked_icon=None,
                 greyed_checked_icon=None,node_class=None, drop_callback=None,
                 node_select_callback=None,
                 *args, **kw_args):

        Frame.__init__(self, master=master)

        self.tree=MultiSelectTree(self, root_id, root_label,
                 get_contents_callback, dist_x, dist_y,
                 text_offset, line_flag, expanded_icon,
                 collapsed_icon, regular_icon, plus_icon,
                 minus_icon, node_class,drop_callback = drop_callback,
                 node_select_callback=node_select_callback,
                 *args, **kw_args)

        self.tree.grid(row=0, column=0, sticky='nsew')

        # make expandable
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # add scrollbars
        sb=Scrollbar(self)
        sb.grid(row=0, column=1, sticky='ns')
        self.tree.configure(yscrollcommand=sb.set)
        sb.configure(command=self.tree.yview)

        sb=Scrollbar(self, orient=HORIZONTAL)
        sb.grid(row=1, column=0, sticky='ew')
        self.tree.configure(xscrollcommand=sb.set)
        sb.configure(command=self.tree.xview)

        # must get focus so keys work for demo
        self.tree.focus_set()

    def getPreviousSelectedNode(self):
        return self.tree.getPreviousSelectedNode()

    def getSelectedNode(self):
        return self.tree.getSelectedNode()

    def saveNodesToFile(self, fileName):
        self.tree.saveNodesToFile(fileName)

    def loadNodesFromFile(self, fileName):
        self.tree.loadNodesFromFile(fileName)

    def expandRoot(self):
        self.tree.expandRoot()

    def collapseRoot(self):
        self.tree.collapseRoot()

    def deleteSelectedNode(self):
        self.tree.deleteSelectedNode()

    def createNode(self, name, expandable, parentFullId, expanded, selected):
        self.tree.createNode(name, expandable, parentFullId, expanded, selected)

    def moveCursor(self, node):
        self.tree.move_cursor(node)

    def getPath(self, fullId):
        return self.tree.separater.join(fullId)

