from Tree import Tree, Node, Struct
from Tix import PhotoImage
import pickle

class MultiSelectNode(Node):
    """Extended Node class to allow selection of the node and its subtree"""
    def __init__(self, parent_node, id, collapsed_icon, x, y,
                 parent_widget=None, expanded_icon=None, label=None,
                 expandable_flag=0, draw=True):
        """overridden method (Node)"""

        # Call the constructor of Node
        Node.__init__(self, parent_node, id, collapsed_icon, x, y,
                 parent_widget, expanded_icon, label, expandable_flag)

        # Add additional functionality to Node to allow selection of nodes and their subtrees
        self.x = x
        self.y = y

        self.selected = False

        sw = self.widget

        self.checkUncheckImage = sw.create_image(x - sw.realDistX, y, image=sw.uncheckedIcon)
        sw.tag_bind(self.checkUncheckImage, '<1>', self._selectNode)
        sw.tag_bind(self.checkUncheckImage, '<3>', self._selectNode2)

        sw.tag_bind(self.symbol, '<1>', self._onNodeSelect)
        sw.tag_bind(self.label, '<1>', self._onNodeSelect)

        self.toBeExpanded = False

    def _onNodeSelect(self, event):
        """Move cursor and perform external function if required"""
        sw = self.widget
        sw.move_cursor(self)

        if sw.nodeSelectCallback:
            sw.nodeSelectCallback(self)

    def delete(self, meToo=1):
        """overridden method (Node)"""

        # First clean up what additional stuff was added
        if meToo:
            print ("MultiSelectNode deleting checkUncheckImage")
            self.widget.delete(self.checkUncheckImage)

        # Then call the parent class' method
        Node.delete(self, meToo)

    def PVT_delete_subtree(self):
        """overridden method (Node)"""

        # First clean up what additional stuff was added
        for i in self.child_nodes:
            self.widget.delete(i.checkUncheckImage)

        # Then call the parent class' method
        Node.PVT_delete_subtree(self)

    def PVT_click(self, event):
        """overridden method (Node)"""

        Node.PVT_click(self, event)

        if self.widget.drop_callback:
            #TODO: figure out if anything is needed here to support dnd
            pass
        else:
            # Propogate the changes to the structure stored in Tree so that the changes are
            # not lost on minimising a node
            self.widget.setSavedNodeExpanded(self)

            if self.expanded():
                self._fixExpandedChildren()

    def expand(self):
        Node.expand(self)
        self._fixExpandedChildren()

    def _fixExpandedChildren(self):
        """This method is needed to expand those children of a node that were marked for expansion
           when the parent was being expanded."""

        # They could not be expanded during the expansion of the parent node since the method PVT_set_state
        # which performs the actual expansion has a mutex to prevent another thread from expanding.
        for child in self.child_nodes:
            if child.toBeExpanded:
                child.toBeExpanded = False
                child.expand()

                child._fixExpandedChildren()

    def PVT_insert(self, nodes, pos, below):
        """overridden method (Node)"""
        Node.PVT_insert(self, nodes, pos, below)

        # Select the nodes and expand them if required.
        for i in range(len(nodes)):
            node = nodes[i]
            self.child_nodes[pos + i].setSelected(0)

            if (node.expanded):
                # We can't expand these nodes now since the mutex in PVT_set_state is locked
                # Hence mark them for exmapsion. They will be fixed in the click handler.
                self.child_nodes[pos + i].toBeExpanded = True

    def setSelected(self, selected):
        """Change the state of the node to selected, not selected or mixed"""
        self.selected = selected

        self._showCheckedImage()

    def _showCheckedImage(self):
        """Show the appropriate image depending on whether the node is selected or not"""
        sw = self.widget

        if self.selected:
            image=sw.checkedIcon
        elif self.selected is None:
            image = sw.greyedCheckedIcon
        else:
            image=sw.uncheckedIcon

        sw.itemconfig(self.checkUncheckImage, image=image)

    def _selectNode(self, event):
        """Handle mouse click event on the checkUncheckImage"""

        # WE USE A DIFFERENT NOTION: A THICK CHECK MARK MEANS, DO RECURSIVELY ADD, A THIN CHECK MARK, MEANS ADD ONLY FILES
        # IN THIS DIRECTORY


        # Toggle the node's selected checkbox
        if self.selected == None:
           selected = 0
        elif not self.selected:
           selected = 1
        else:
           selected = None

        self.setSelected(selected)

        #   selected = self.selected == None or not self.selected


        # Set the node and its children to the selected value specified recursively
        #self._setSelectedRecursively(selected)

        # Set the ancestors' selecetd checkboxes to greyed out or to that of the child
        # depending on whether the children of a parent have different values or the same
        #self._setAncestorsSelected()

        # Propogate the changes to the structure stored in Tree so that the changes are
        # not lost on minimising a node
        self.widget.setSavedNodeSelected(self)

    def _selectNode2(self, event):
        """Handle mouse click event on the checkUncheckImage"""

        # WE USE A DIFFERENT NOTION: A THICK CHECK MARK MEANS, DO RECURSIVELY ADD, A THIN CHECK MARK, MEANS ADD ONLY FILES
        # IN THIS DIRECTORY


        # Toggle the node's selected checkbox
        if self.selected == None:
           selected = 0
        elif not self.selected:
           selected = 1
        else:
           selected = None

        self.setSelected(selected)

        #   selected = self.selected == None or not self.selected


        # Set the node and its children to the selected value specified recursively
        if (selected == None):
           for child in self.child_nodes:
              child.setSelected(1)
        elif (selected == 1):
           for child in self.child_nodes:
              child.setSelected(0)
        else:
           for child in self.child_nodes:
              child.setSelected(None)

        # Set the ancestors' selecetd checkboxes to greyed out or to that of the child
        # depending on whether the children of a parent have different values or the same
        #self._setAncestorsSelected()

        # Propogate the changes to the structure stored in Tree so that the changes are
        # not lost on minimising a node
        self.widget.setSavedNodeSelected(self)

    def _setSelectedRecursively(self, selected):
        """Set the node and all its children to the value specified"""
        self.setSelected(selected)

        if (selected == None):
           selected = 0

        for child in self.child_nodes:
            child._setSelectedRecursively(selected)

    def _setAncestorsSelected(self):
        """Set all the node's ancestors' selected value based on the node's selected value"""
        ancestor = self.parent_node

        while ancestor:
            if ancestor._allChildrenSame(self.selected):
                ancestor.setSelected(self.selected)
            else:
                ancestor.setSelected(None)

            ancestor = ancestor.parent_node

    def _allChildrenSame(self, selected):
        """Returns whether all children of the node have the selected value as the one specified"""
        for child in self.child_nodes:
            if child.selected != selected:
                return False

        return True

class MultiSelectTree(Tree):
    """Extended Tree class to allow selection of nodes and subtrees.
       Additional parameters:
        unchecked_icon - Icon to show when a node (and each of its children) is unchecked.
        checked_icon - Icon to show when a node (and each of its children) is checked.
        greyed_checked_Icon - icon to show when some children of a node are checked and others are not.
        node_select_callback - A method to call back when a node is selected. No action will be performed if it is None.
       Useful attribuets:
        savedNodesMap - This structure is used to remember nodes and their selected/expanded states"""
    def __init__(self, master, root_id, root_label='',
                 get_contents_callback=None, dist_x=15, dist_y=15,
                 text_offset=10, line_flag=1, expanded_icon=None,
                 collapsed_icon=None, regular_icon=None, plus_icon=None,
                 minus_icon=None, unchecked_icon=None, checked_icon=None,
                 greyed_checked_icon=None,node_class=MultiSelectNode, drop_callback=None,
                 node_select_callback=None,
                 *args, **kw_args):

        self.separater = ' -> '

        self.pos = None

        self.rootId = root_id
        self.realDistX = dist_x

        self.nodeSelectCallback = node_select_callback

        if checked_icon == None:
            self.checkedIcon=PhotoImage(file='checkedIcon.gif')
        else:
            self.checkedIcon=checked_icon
        if unchecked_icon == None:
            self.uncheckedIcon=PhotoImage(file='uncheckedIcon.gif')
        else:
            self.uncheckedIcon=unchecked_icon
        if greyed_checked_icon == None:
            self.greyedCheckedIcon=PhotoImage(file='greyedIcon.gif')
        else:
            self.greyedCheckedIcon=greyed_checked_icon

        if get_contents_callback == None:
            get_contents_callback = self._getContents

        savedNode = Struct()
        savedNode.name = self.rootId
        savedNode.expandable = True
        savedNode.fullPath = self.rootId
        savedNode.expanded = False
        savedNode.selected = False

        # This structure is used to remember selected nodes and their selected/expanded states
        self.savedNodesMap = {'': [savedNode], savedNode.fullPath: []}

        Tree.__init__(self, master, root_id, root_label,
                 get_contents_callback, dist_x * 2, dist_y,
                 text_offset, line_flag, expanded_icon,
                 collapsed_icon, regular_icon, plus_icon,
                 minus_icon, node_class, drop_callback,
                 *args, **kw_args)

    def add_node(self, name=None, id=None, flag=0, expanded_icon=None,
                 collapsed_icon=None, selected=False, expanded=False,
                 full_parent_id=()):
        """overridden method (Tree)"""
        Tree.add_node(self, name, id, flag, expanded_icon, collapsed_icon)

        fullParentPath = self.separater.join(full_parent_id)

        if fullParentPath not in self.savedNodesMap.keys():
            self.savedNodesMap[fullParentPath] = []

        savedNode = self._getSavedNode(fullParentPath, name)
        if savedNode is not None:
            self.new_nodes[-1].selected = savedNode.selected
            self.new_nodes[-1].expanded = savedNode.expanded

            return

        savedParentNode = self._getSavedNode(self.separater.join(full_parent_id[0:len(full_parent_id) - 1]), full_parent_id[-1])

        node = Struct()
        node.name = name
        node.expandable = flag
        node.fullPath = self.separater.join(full_parent_id + (id,))
        node.expanded = expanded
        node.selected = savedParentNode.selected

        self.savedNodesMap[fullParentPath].append(node)

        self.new_nodes[-1].selected = node.selected
        self.new_nodes[-1].expanded = node.expanded

    def move_cursor(self, node):
        """overridden method (Tree)"""

        # save the old position
        self.oldPos = self.pos

        Tree.move_cursor(self, node)

    def _addFromSavedNode(self, savedNode):
        """Adds the node to new_nodes list from the savedNodesMap structure"""
        Tree.add_node(self, savedNode.name, savedNode.name, savedNode.expandable, None, None)

        self.new_nodes[-1].selected = savedNode.selected
        self.new_nodes[-1].expanded = savedNode.expanded

    def _getContents(self, node):
        """Gets the node information from the savedNodesMap and calls appropriate methods
           to add the node to the new_nodes list that will be used to create the node on the UI"""
        nodeId = node.full_id()
        path=self.separater.join(nodeId)

        if path not in self.savedNodesMap:
            return

        for savedChildNode in self.savedNodesMap[path]:
            node.widget._addFromSavedNode(savedChildNode)

    def setSavedNodeExpanded(self, node):
        """Updates the expanded value in the cached savedNodesMap for the node specified"""
        if node.parent_node == None:
            parentPath = ''
        else:
            parentPath = self.separater.join(node.parent_node.full_id())

            sibling = self._getSavedNode(parentPath, node.id)

            sibling.expanded = node.expanded()

    def setSavedNodeSelected(self, node):
        """Updates the selected value in the cached savedNodesMap for the node specified"""
        if node.parent_node == None:
            parentPath = ''
        else:
            parentPath = self.separater.join(node.parent_node.full_id())

        savedNode = self._getSavedNode(parentPath, node.id)

        savedNode.selected = node.selected
        self._setSavedChildrenSelected(savedNode)
        self._setSavedAncestorsSelected(savedNode.fullPath.split(self.separater)[:-1], savedNode.selected)

    def _getSavedNode(self, parentPath, name):
        """Gets the saved node from the savedNodesMap given the parent's path for the name specified"""
        for sibling in self.savedNodesMap[parentPath]:
            if sibling.name == name:
                return sibling

        #TODO: Raise an exception

    def _setSavedChildrenSelected(self, savedNode):
        """Sets the selected value of the children of the node appropriately"""
        if savedNode.fullPath not in self.savedNodesMap.keys():
            return

        for savedChildNode in self.savedNodesMap[savedNode.fullPath]:
            savedChildNode.selected = savedNode.selected
            self._setSavedChildrenSelected(savedChildNode)

    def _setSavedAncestorsSelected(self, hierarchy, selected):
        """Sets the selected value of the ancestors of the node appropriately"""

        for i in reversed(range(len(hierarchy))):
            ancestorParentPath = self.separater.join(hierarchy[:i])

            ancestor = self._getSavedNode(ancestorParentPath, hierarchy[i])

            if self._allSavedChildrenSame(ancestor, selected):
                ancestor.selected = selected
            else:
                ancestor.selected = None

    def _allSavedChildrenSame(self, ancestor, selected):
        """Checks whether all children of a node have the same selected value as the one specified"""
        if not ancestor.expandable:
            return True

        for savedChild in self.savedNodesMap[ancestor.fullPath]:
            if selected is None:
                selected = savedChild.selected

            if savedChild.selected != selected:
                return False

        return True

    def createNode(self, name, expandable, parentFullId, expanded, selected):
        node = Struct()
        node.name = name
        node.expandable = expandable
        node.fullPath = self.separater.join(parentFullId + (node.name,))
        node.expanded = expanded
        node.selected = selected

        self.savedNodesMap[self.separater.join(parentFullId)].append(node)

        grandParentPath = self.separater.join(parentFullId[:-1])

        parentSavedNode = self._getSavedNode(grandParentPath, parentFullId[-1])

        parentSavedNode.expandable = True

        parentSavedNode.expanded = True

        self.savedNodesMap[node.fullPath] = []

    def deleteSelectedNode(self):
        nodeId = self.pos.full_id()

        parentPath = self.separater.join(nodeId[:-1])

        deletedNode = self._getSavedNode(parentPath, self.pos.id)
        selected = deletedNode.selected

        if selected is not None:
            selected = not selected

        self.savedNodesMap[parentPath].remove(deletedNode)

        self._deleteNodesRecursively(self.separater.join(nodeId))

        self._setSavedAncestorsSelected(nodeId[:-1], selected)

        self.root.setSelected(self.savedNodesMap[''][0].selected)

    def _deleteNodesRecursively(self, fullPath):
        if fullPath not in self.savedNodesMap.keys():
            return

        for savedNode in self.savedNodesMap.pop(fullPath):
            self._deleteNodesRecursively(savedNode.fullPath)

    def createDummyTree(self):

        node = Struct()
        node.name = 'Analytics'
        node.expandable = True
        node.fullPath = self.separater.join((self.rootId, node.name))
        node.expanded = False
        node.selected = False

        self.savedNodesMap[self.rootId] = [node]

        node = Struct()
        node.name = 'Master Admin'
        node.expandable = False
        node.fullPath = self.separater.join((self.rootId, node.name))
        node.expanded = False
        node.selected = False

        self.savedNodesMap[self.rootId].append(node)

        self.savedNodesMap[self.separater.join((self.rootId, 'Analytics'))] = []

        node = Struct()
        node.name = 'Some test case'
        node.fullPath = self.separater.join((self.rootId, 'Analytics', node.name))
        node.expandable = False
        node.expanded = False
        node.selected = False

        self.savedNodesMap[self.separater.join((self.rootId, 'Analytics'))].append(node)

        node = Struct()
        node.name = 'testing'
        node.fullPath = self.separater.join((self.rootId, 'Analytics', node.name))
        node.expandable = True
        node.expanded = False
        node.selected = False

        self.savedNodesMap[self.separater.join((self.rootId, 'Analytics'))].append(node)

        node = Struct()
        node.name = 'Some test case'
        node.fullPath = self.separater.join((self.rootId, 'Analytics', 'testing', node.name))
        node.expandable = False
        node.expanded = False
        node.selected = False

        self.savedNodesMap[self.separater.join((self.rootId, 'Analytics', 'testing'))] = [node]

    def getPreviousSelectedNode(self):
        return self.oldPos

    def getSelectedNode(self):
        return self.pos

    def expandRoot(self):
        self.root.expand()

    def collapseRoot(self):
        self.root.collapse()

    def saveNodesToFile(self, fileName):
        nodesFile = open(fileName, 'wb')
        pickle.dump(self.savedNodesMap, nodesFile)
        nodesFile.close()

    def loadNodesFromFile(self, fileName):
        nodesFile = open(fileName, 'rb')
        self.savedNodesMap = pickle.load(nodesFile)
        nodesFile.close()

        self.root.setSelected(self.savedNodesMap[''][0].selected)

# the good 'ol test/demo code
if __name__ == '__main__':
    import os
    import sys
    from Tix import *

    # default routine to get contents of subtree
    # supply this for a different type of app
    # argument is the node object being expanded
    # should call add_node()
    def get_contents(node):
        path=os.path.join(*node.full_id())
        for filename in os.listdir(path):
            full=os.path.join(path, filename)
            name=filename
            folder=0
            if os.path.isdir(full):
                # it's a directory
                folder=1
            elif not os.path.isfile(full):
                # but it's not a file
                name=name+' (special)'
            if os.path.islink(full):
                # it's a link
                name=name+' (link to '+os.readlink(full)+')'
            node.widget.add_node(name=name, id=filename, flag=folder,full_parent_id=node.full_id())

    root=Tk()
    root.title(os.path.basename(sys.argv[0]))
    tree=os.sep
    if sys.platform == 'win32':
        # we could call the root "My Computer" and mess with get_contents()
        # to return "A:", "B:", "C:", ... etc. as it's children, but that
        # would just be terminally cute and I'd have to shoot myself
        tree='C:'+os.sep

    # create the control
    t=MultiSelectTree(master=root,
           root_id=tree,
           root_label=tree,
           get_contents_callback=get_contents,
           width=300)
    t.grid(row=0, column=0, sticky='nsew')

    # make expandable
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # add scrollbars
    sb=Scrollbar(root)
    sb.grid(row=0, column=1, sticky='ns')
    t.configure(yscrollcommand=sb.set)
    sb.configure(command=t.yview)

    sb=Scrollbar(root, orient=HORIZONTAL)
    sb.grid(row=1, column=0, sticky='ew')
    t.configure(xscrollcommand=sb.set)
    sb.configure(command=t.xview)

    # must get focus so keys work for demo
    t.focus_set()

    # we could do without this, but it's nice and friendly to have
    Button(root, text='Quit', command=root.quit).grid(row=2, column=0,
                                                      columnspan=2)

    # expand out the root
    t.root.expand()

    root.mainloop()
