from collections import deque

class Visitor(object):

    def visit(self, node, context=None):
        pass

    def children(self, node):
        return node.children[:]
    
    def is_leaf(self, node):
        return len(node.children) == 0

    def finalize(self):
        pass

    def simple_bfs(self, node):
        """
        Breadth-first search
        """
        dq = deque([node])
        while dq:
            current = dq.popleft()
            self.visit(current)
            dq.extend(self.children(current))
        return self.finalize()

    def simple_xbfs(self, node):
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

    def simple_dfs_preorder(self, node):
        """
        Depth-first search - preorder
        """
        dq = deque([node])
        while dq:
            current = dq.pop()
            self.visit(current)
            for c in reversed(self.children(current)):
                dq.append(c)
        return self.finalize()

    simple_dfs = simple_dfs_preorder

    def simple_dfs_postorder(self, node):
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

    def retval_dfs_postorder(self, node):
        """
        Depth-first search - postorder
        """
        retval = [[]]
        expanded = set()
        dq = deque([node])
        while dq:
            current = dq[-1]
            if id(current) in expanded:
                dq.pop()
                _vals = retval.pop()
                retval[-1].append( self.visit(current, _vals) )
            elif self.is_leaf(current):
                dq.pop()
                retval[-1].append( self.visit(current) )
            else:
                for c in reversed(self.children(current)):
                    dq.append(c)
                expanded.add(id(current))
                retval.append( [] )
        return self.finalize()

    def simple_dfs_inorder(self, node):
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


"""
#---------
# TEST
#---------
import sys

class CountVisitor(Visitor):

    def __init__(self):
        self.count = 0

    def visit(self, node):
        self.count += 1
        node.num = self.count


class PrintVisitor(Visitor):

    def visit(self, node):
        sys.stdout.write("%d " % node.num)
        
    def finalize(self):
        sys.stdout.write("\n")


class PPrintVisitor(Visitor):

    def visit(self, node):
        if self.is_leaf(node):
            return
        sys.stdout.write("%d :" % node.num)
        for c in self.children(node):
            sys.stdout.write(" %d" % c.num)
        sys.stdout.write("\n")
        

class SumVisitor(Visitor):

    def __init__(self):
        self.count = 0

    def visit(self, node, context=None):
        if context is None or len(context) == 0:
            self.count = node.num
        else:
            self.count = node.num + sum(context)
        return self.count
    
    def finalize(self):
        return self.count


cvisitor = CountVisitor()
pvisitor = PrintVisitor()
ppvisitor = PPrintVisitor()
svisitor = SumVisitor()


class Node(object):

    def __init__(self):
        self.children = []
        self.num = 0

    def __str__(self):
        return str(self.num)

root = Node()
root.children = [Node(), Node(), Node()]
root.children[0].children = [Node(), Node(), Node()]
root.children[0].children[0].children = [Node(), Node(), Node()]
root.children[0].children[1].children = [Node(), Node(), Node()]
root.children[0].children[2].children = [Node(), Node(), Node()]
root.children[1].children = [Node(), Node(), Node()]
root.children[1].children[0].children = [Node(), Node(), Node()]
root.children[1].children[1].children = [Node(), Node(), Node()]
root.children[1].children[2].children = [Node(), Node(), Node()]
root.children[2].children = [Node(), Node(), Node()]
root.children[2].children[0].children = [Node(), Node(), Node()]
root.children[2].children[1].children = [Node(), Node(), Node()]
root.children[2].children[2].children = [Node(), Node(), Node()]

cvisitor.simple_bfs(root)

print("BFS")
pvisitor.simple_bfs(root)
print("DFS PreOrder")
pvisitor.simple_dfs(root)
print("DFS InOrder")
pvisitor.simple_dfs_inorder(root)
print("DFS PostOrder")
pvisitor.simple_dfs_postorder(root)

print("SUM %d" % svisitor.retval_dfs_postorder(root))
ppvisitor.simple_bfs(root)
ppvisitor.simple_xbfs(root)

"""
