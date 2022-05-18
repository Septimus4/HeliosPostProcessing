import osmnx as ox

try:
	from Scripts.MapToPy.utils import JsonWriter,Visu,calcRatio,shortListByPath
except ImportError:
	from utils import JsonWriter,Visu,calcRatio,shortListByPath

class GenGraph:
	def __init__(self,addr,angle,height):
		self.lat,self.lon = addr[0],addr[1]
		self.angle,self.height=angle,height

	@staticmethod
	def findBoxCoo(lat, lon, angle, height):
		base_ratio = 0.002651
		surf = calcRatio(angle, height)
		ratio=(surf*base_ratio)/1500
		return [ lat+ratio,lat-ratio,lon+ratio,lon-ratio ]

	def run(self,):
		return ox.graph_from_bbox(
			*self.findBoxCoo( self.lat,self.lon,self.angle,self.height ) )\
			.to_undirected()

class PreProcessGraph:
	def __init__(self,graph):
		self.G = graph
		self.e_names = self.G.edges.data('name')
		self.n_names = self.G.nodes.data()

	@staticmethod
	def _getRecElem(func,felem,selem,idx):
		if len(idx)<=0:
			return [felem,selem]
		f_idx,s_idx=idx.pop()
		felem=felem[f_idx]
		selem=selem[s_idx]
		return func(func,felem,selem,idx)

	def ppret(self,data,keyidx,elemidx):
		itNone=0
		res = {}
		for i in data:
			f_elem,s_elem=self._getRecElem(
				self._getRecElem,i,i,list(elemidx))
			t_kidx = i[keyidx]
			if type(t_kidx)==list:
				t_kidx=t_kidx[0]
			if t_kidx not in res.keys():
				res[t_kidx]=[]
			elif t_kidx==None:
				res['None'+str(itNone)]=[]
				t_kidx='None'+str(itNone)
				itNone+=1
			res[t_kidx].append( [f_elem,s_elem] )
		return res

	def ppIdToCoo(self,):
		res={}
		for key,i in self.st_names.items():
			if key not in res.keys():
				res[key]=[]
			for it in i:
				res[key].append(
					[*self.inter_pts[it[0]],
					*self.inter_pts[it[1]]])
		return res

	def run(self,):
		self.inter_pts = self.ppret(
			self.n_names,0,[('x','y'),(1,1)] )
		self.st_names = self.ppret(
			self.e_names,2,[(0,1)] )
		self.st_names = shortListByPath(self.st_names)
		return self.ppIdToCoo()

class PixTransform:
	def __init__(self,data,m_shape):
		self.data = data
		self.m_shape = m_shape

	def equivPixel(self,):
		def clearDataset(data):
			x,y=[],[]
			for i in data.values():
				x+=[ j[0] for t_i in i for j in t_i ]
				y+=[ j[1] for t_i in i for j in t_i ]
			return min(x),max(x),min(y),max(y)
		xmin,xmax,ymin,ymax = clearDataset(self.data)
		x_diff,y_diff = xmax-xmin,ymax-ymin
		xratio,yratio=(x_diff/self.m_shape[0]),(y_diff/self.m_shape[1])
		self.xcoo,self.ycoo=[ xmin+(i*xratio) for i in range(self.m_shape[0]) ],\
			[ ymin+(i*yratio) for i in range(self.m_shape[1]) ]

	def buildPixTab(self,):
		def getEquiv(v,tab):
			for it,i in enumerate(tab):
				if i>=v:
					return it
			return len(tab)
		pix = {}
		for key,i in self.data.items():
			pix[key]=[ [[getEquiv(it[0][0],self.xcoo),getEquiv(it[0][1],self.ycoo)],\
				[getEquiv(it[1][0],self.xcoo),getEquiv(it[1][1],self.ycoo)]]\
					for it in i ]
		return pix

	def run(self,):
		self.equivPixel()
		return self.buildPixTab()

def graphWrap(addr,shape,path,isView=False):
	G = GenGraph(addr,84,60).run()
	names_coo = PreProcessGraph(G).run()
	m_pix = PixTransform(names_coo,shape).run()
	if isView:
		Visu.showMap( m_pix )
	JsonWriter( path+'.json',m_pix ).run()

def main():
	graphWrap( [43.854472,1.807545],(300,300),'./DataOut/outlisle.json',True ) #Lisle sur Tarn (vers la gare)

if __name__ == "__main__":
	main()