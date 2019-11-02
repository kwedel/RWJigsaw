import numpy as np
import matplotlib.pyplot as plt
import svgwrite

class Dot:
    '''Class containing data for a single dot in the puzzle.
    Initiate with coordinates i,j'''
    def __init__(self,i,j):
        self.color = None
        self.active = True
        self.empty = True
        self.coords = (i,j)
        self.free_neighbors = []
        self.bonds = []
        self.neighbors = [tuple(np.array(self.coords) + shift)
                          for shift in
            [(1, 1),(-1, 1),(-1, -1),(1, -1)]]
    
    def __repr__(self):
        return f'coords: {self.coords}, color: {self.color}\nactive: {self.active}, empty: {self.empty}'
    
def get_color(Dot):
    if Dot.empty:
        if not Dot.active:
            return -1
        else:
            return 0
    return Dot.color
    
class Jigsaw:
    '''Class for a random walk jigsaw

    Parameters
    ----------
    res : int
        Resolution of grid. Two cells are taken for border.
    bordertype : string
        'rect' for a square puzzle.
        'circ' for a circular puzzle.
'''
    def __init__(self,res=50,bordertype='rect'):
        self.res = res + 2
        self.num_pieces = 0
        self.jigsaw = np.zeros((self.res,self.res),dtype=Dot)
        for i in range(self.res):
            for j in range(self.res):
                self.jigsaw[i,j] = Dot(i,j)
        self.active_cells = []
        if bordertype=='circ':
            self.circle_mask()
        else:
            self.border_mask()
        
    def border_mask(self):
        '''Creates a square border on the outermost rows/columns'''
        for i in range(self.res):
            for x,y in [(i,0),(i,-1),(0,i),(-1,i)]:
                self.jigsaw[x,y].active = False
                self.jigsaw[x,y].empty = False
                
    def circle_mask(self):
        '''Create a circular border'''
        for i in range(self.res):
            for j in range(self.res):
                x = i-self.res/2 + 1/2
                y = j-self.res/2 + 1/2
                if np.sqrt(x**2 + y**2) > self.res/2 - 1.1:
                    self.jigsaw[i,j].active = False
                    self.jigsaw[i,j].empty = False
        
    def initiate_pieces(self,num_pieces=11, min_dist=1):
        '''Initiate a number of pieces by randomly filling empty squares.
        Use min_dist to spread out seeding points. Be careful, it might
        not converge.
'''
        self.num_pieces = num_pieces
        
        for c in range(1, self.num_pieces+1):
            d = Dot(0,0)
            d.empty=False
            n = 0
            while not (d.empty and d.active) and n<1000:
                n += 1
                index = tuple(np.random.choice(self.res, 2))
                too_close = False
                for p in self.active_cells:
                    dist = np.sqrt(np.sum((np.array(index) - np.array(p))**2))
                    if dist < min_dist:
                        too_close = True
                        break
                if too_close:
                    continue
                d = self.jigsaw[index]
                if d.empty and d.active:
                    d.color = c
                    d.empty = False
                    self.active_cells.append(d.coords)
                    break
                    
    def step(self, grow_prop=1, verbose=False):
        '''Grow all active, occupied cells with probability grow_prop'''
        if verbose: print(f'Number of active cells: {len(self.active_cells)}')
        new_active_cells = []
        np.random.shuffle(self.active_cells)
        for coo in self.active_cells:
            d = self.jigsaw[coo]
            # Check if any neighbor cells are free
            d.free_neighbors = []
            for i,n in enumerate(d.neighbors):
                if self.jigsaw[n].empty:
                    d.free_neighbors.append(i)
            d.free_neighbors = np.array(d.free_neighbors)
            # Check for bonds blocking free neighbors
            upper_n = self.jigsaw[tuple(d.coords + np.array([0,1]))]
            lower_n = self.jigsaw[tuple(d.coords + np.array([0,-1]))]
            if 3 in upper_n.bonds:
                d.free_neighbors = d.free_neighbors[d.free_neighbors != 0]
            if 2 in upper_n.bonds:
                d.free_neighbors = d.free_neighbors[d.free_neighbors != 1]
            if 1 in lower_n.bonds:
                d.free_neighbors = d.free_neighbors[d.free_neighbors != 2]
            if 0 in lower_n.bonds:
                d.free_neighbors = d.free_neighbors[d.free_neighbors != 3]
            if d.free_neighbors.size == 0:
                d.active = False
                continue
            # Choose an neighbor
            nb_idx = np.random.choice(d.free_neighbors, 1)[0]
            if np.random.rand() < grow_prop:
                newlink = self.jigsaw[d.neighbors[nb_idx]]
                newlink.color = d.color
                newlink.active = True
                newlink.empty = False
                newlink.bonds.append((nb_idx+2) % 4)
                d.bonds.append(nb_idx)
                new_active_cells.append(d.neighbors[nb_idx])
                
            new_active_cells.append(coo)
        self.active_cells = new_active_cells
                
                
    def steps(self,steps=500, **kwargs):
        '''Loop function for taking multiple steps'''
        for _ in range(steps):
            self.step(**kwargs)
            if not self.active_cells:
                print(f'Converged at step {_}')
                break
        else:
            print(f'Did not converge in {steps} steps.')
        
    def complete(self):
        '''Fill in the rest of the puzzle with what should be
        parts of the border. This helps when exporting.
        '''
        for i in range(self.res):
            for j in range(self.res):
                d = self.jigsaw[(i,j)]
                if d.empty and d.active:
                    d.empty = False
                    d.color = 1000
                    self.active_cells.append((i,j))
                    self.steps(1000)
                
    def show(self):
        '''Show puzzle'''
        plt.figure(figsize=(7,7))
        plt.subplot(aspect=1)
        for i in range(self.res):
            for j in range(self.res):
                d = self.jigsaw[(i,j)]
                if 2 in d.bonds:
                    plt.plot([i, i-1], [j, j-1],f'C{d.color % 9}o-')
                if 3 in d.bonds:
                    plt.plot([i, i+1], [j, j-1],f'C{d.color % 9}o-')
        plt.show()
    
    def _draw_arc(self,x,y,r,quad,stroke_width=4):
        '''Returns an svg quarter circle using the svgwrite module

        Parameters
        ----------
        x,y : the circle center
        r : is the radius
        quad : the quadrant of the quarter circle
        stroke_width : width of svg stroke
        '''
        if quad in [0, 1]:
            yshift = r
        else:
            yshift = -r
        if quad in [0,3]:
            xshift = r
        else:
            xshift = -r
        flip = 0
        if quad in [1,3]:
            flip = 1
        return svgwrite.Drawing().path(d=f'M {x} {y+yshift} a {r},{r} 0 0,{flip} {xshift} {-yshift}',
                                      stroke='black',
                                      fill='none',
                                      style=f'stroke-width:{stroke_width}')
    
    def export(self,filename='out.svg', scale=15, **kwargs):
        '''Export puzzle as svg

        Inputs
        ------
        filename : filename to save svg file to
        scale : diameter of circles in px
        stroke_width : width of stroke in svg
        '''
        colormap = plt.cm.get_cmap('jet',self.num_pieces)
        svg = svgwrite.Drawing(filename=filename, size=(scale*self.res,scale*self.res))
        g_circles = svg.add(svg.g(id='circles'))
        g_strokes = svg.add(svg.g(id='strokes'))
        for i in range(self.res):
            for j in range(self.res):
                d = self.jigsaw[(i,j)]
                if not d.color:
                    continue
                nobonds = set(range(4)) - set(d.bonds)
                for quad in nobonds:
                    g_strokes.add(self._draw_arc(i*scale,j*scale, scale/2, quad, **kwargs))
                if d.color == 1000:
                    fill = '#FFFFFF'
                else:
                    fill = cmap_to_hex(colormap(d.color))
                g_circles.add(svg.circle((scale*i,scale*j),scale/2.1,
                                   fill=fill))
        svg.save()
        print(f'File saved to {filename}')
        return svg
    
    def count(self):
        '''Show sizes of puzzle pieces'''
        counts = {}
        for x in range(self.res):
            for y in range(self.res):
                d = self.jigsaw[x,y]
                try:
                    counts[d.color] += 1
                except:
                    counts[d.color] = 1
        del counts[None]
        print('    Piece   Size')
        for p,n in sorted(counts.items()):
            print(f'{p:9} {n:6}')
        return counts

    def __repr__(self):
        return f'Resolution: {self.res}, number of pieces: {self.num_pieces}'

def cmap_to_hex(tup):
    '''Convert rgb from (0.5,0.5,0.5) format to hex'''
    return '#%02x%02x%02x' % tuple([int(t*255) for t in tup[:-1]])
