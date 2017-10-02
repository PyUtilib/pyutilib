from collections import deque

class SimpleVisitor(object):

    def visit(self, node):
        pass

    def children(self, node):
        return node.children
    
    def is_leaf(self, node):
        return len(node.children) == 0

    def finalize(self):
        pass

    def bfs(self, node):
        """
        Breadth-first search
        """
        dq = deque([node])
        while dq:
            current = dq.popleft()
            self.visit(current)
            if not self.is_leaf(current):
                dq.extend(self.children(current))
        return self.finalize()

    def xbfs(self, node):
        """
        Breadth-first search, except that 
        leaf nodes are immediately visited.
        """
        dq = deque([node])
        while dq:
            current = dq.popleft()
            self.visit(current)
            for c in self.children(current):
                if self.is_leaf(c):
                    self.visit(c)
                else:
                    dq.append(c)
        return self.finalize()

    def dfs_preorder(self, node):
        """
        Depth-first search - preorder
        """
        dq = deque([node])
        while dq:
            current = dq.pop()
            self.visit(current)
            if not self.is_leaf(current):
                for c in reversed(self.children(current)):
                    dq.append(c)
        return self.finalize()

    dfs = dfs_preorder

    def dfs_postorder(self, node):
        """
        Depth-first search - postorder
        """
        expanded = set()
        dq = deque([node])
        while dq:
            current = dq[-1]
            if id(current) in expanded:
                dq.pop()
                self.visit(current)
            else:
                for c in reversed(self.children(current)):
                    dq.append(c)
                expanded.add(id(current))
        return self.finalize()

    def dfs_inorder(self, node):
        """
        Depth-first search - inorder
        """
        expanded = set()
        dq = deque([node])
        while dq:
            current = dq.pop()
            if id(current) in expanded or self.is_leaf(current):
                self.visit(current)
            else:
                first = True
                for c in reversed(self.children(current)):
                    if first:
                        first = False
                    else:
                        dq.append(current)
                    dq.append(c)
                expanded.add(id(current))
        return self.finalize()


class ValueVisitor(object):

    def visit(self, node, values):
        pass

    def children(self, node):
        return node.children
    
    def is_leaf(self, node):
        return len(node.children) == 0

    def finalize(self, ans):
        pass

    def visiting_potential_leaf(self, node, values):
        """ 
        Visiting a potential leaf.

        Return True if the node is not expanded.
        """
        if not self.is_leaf(node):
            return False
        ans = self.visit(node, None)
        if ans is None:
            return False
        values.append( ans )
        return True

    def dfs_postorder_deque(self, node):
        """
        Depth-first search - postorder with a dequeue
        """
        _values = [[]]
        expanded = set()
        dq = deque([node])
        while dq:
            current = dq[-1]
            if id(current) in expanded:
                dq.pop()
                values = _values.pop()
                _values[-1].append( self.visit(current, values) )
            elif self.visiting_potential_leaf(current, _values[-1]):
                dq.pop()
            else:
                for c in reversed(self.children(current)):
                    dq.append(c)
                expanded.add(id(current))
                _values.append( [] )
        return self.finalize(_values[-1][0])

    def dfs_postorder_stack(self, node):
        """
        Depth-first search - postorder with a stack
        """
        _stack = [ (node, self.children(node), 0, len(self.children(node)), [])]
        #
        # Iterate until the stack is empty
        #
        # Note: 1 is faster than True for Python 2.x
        #
        while 1:
            #
            # Get the top of the stack
            #   _obj        Current expression object
            #   _argList    The arguments for this expression objet
            #   _idx        The current argument being considered
            #   _len        The number of arguments
            #
            _obj, _argList, _idx, _len, _result = _stack.pop()
            #
            # Iterate through the arguments
            #
            while _idx < _len:
                _sub = _argList[_idx]
                _idx += 1
                if not self.visiting_potential_leaf(_sub, _result):
                    #
                    # Push an expression onto the stack
                    #
                    _stack.append( (_obj, _argList, _idx, _len, _result) )
                    _obj                    = _sub
                    _argList                = self.children(_sub)
                    _idx                    = 0
                    _len                    = len(_argList)
                    _result                 = []
            #
            # Process the current node
            #
            ans = self.visit(_obj, _result)
            if _stack:
                #
                # "return" the recursion by putting the return value on the end of the results stack
                #
                _stack[-1][-1].append( ans )
            else:
                return self.finalize(ans)

