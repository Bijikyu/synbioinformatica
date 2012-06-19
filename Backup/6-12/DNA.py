import re, sys, random
##this code is going be hacky and functional for now... may revisit to make it prettier and more objecty

dna_alphabet = {'A':'A', 'C':'C', 'G':'G', 'T':'T',
                'R':'AG', 'Y':'CT', 'W':'AT', 'S':'CG', 'M':'AC', 'K':'GT',
                'H':'ACT', 'B':'CGT', 'V':'ACG', 'D':'AGT',
                'N':'ACGT',
                'a': 'a', 'c': 'c', 'g': 'g', 't': 't',
                'r':'ag', 'y':'ct', 'w':'at', 's':'cg', 'm':'ac', 'k':'gt',
                'h':'act', 'b':'cgt', 'v':'acg', 'd':'agt',
                'n':'acgt'}


complement_alphabet = {'A':'T', 'T':'A', 'C':'G', 'G':'C','R':'Y', 'Y':'R',
                       'W':'W', 'S':'S', 'M':'K', 'K':'M', 'H':'D', 'D':'H',
                       'B':'V', 'V':'B', 'N':'N','a':'t', 'c':'g', 'g':'c',
                       't':'a', 'r':'y', 'y':'r', 'w':'w', 's':'s','m':'k',
                       'k':'m', 'h':'d', 'd':'h', 'b':'v', 'v':'b', 'n':'n'}


def revcomp(string):
       letters = list(string)
       letters = [complement_alphabet[base] for base in letters]
       rcomp = ''.join(letters)
       return rcomp[::-1] #reverses string

class Overhang(object):
	def __init__(self, seq=""):
		self.sequence = seq

class DNA(object):
	#for linear DNAs, this string should include the entire sequence (5' and 3' overhangs included
	def __init__(self, seq="",DNAclass=""):
		self.sequence = seq
		self.length = len(seq)
		notDNA = re.compile('([^gatcrymkswhbvdn])')
		isnotDNA = False
		exceptionText = "" 
		for m in notDNA.finditer(self.sequence.lower()):
			exceptionText = exceptionText + m.group()+ " at position "+ str( m.start()) + " is not valid IUPAC DNA; "
			isnotDNA = True
		if(isnotDNA):
			raise Exception(exceptionText)
		self.name = "pbca1256" #would be pbca1256 for vectors or pbca1256-Bth8199 for plasmids
		self.description = "SpecR pUC" #this is for humans to read
		self.dam_methylated = True
		self.overhang = "circular" #blunt, 3', 5', circular... should be a class in itself?
		self.topLeftOverhang = ""
		self.bottomLeftOverhang = ""
		self.topRightOverhang = ""
		self.bottomRightOverhang = ""
		#PCR product, miniprep, genomic DNA
		self.provenance = ""
		if DNAclass == "primer" or DNAclass == "genomic" or DNAclass == "PCR product" or DNAclass == "digest":
			self.topology = "linear"
		elif DNAclass == 'plasmid':
			self.topology = "circular" #circular or linear, genomic should be considered linear
		else:
			raise Exception("Invalid molecule class. Acceptable classes are 'digest', genomic', 'PCR product', 'plasmid' and 'primer'.")
	def reversecomp(self):
		return revcomp(self.sequence) #reverses string
		#code to handle the overhangs & other object attributes
	def find(self, string):
		return 0
	def prettyPrint(self):
		#prints out top and bottom strands, truncates middle so length is ~100bp
		#example:
		# TTATCG...[1034bp]...GGAA
		#   ||||              ||||
		#   TAGC..............CCTTAA
		return 0
	
#taken from BioPython
def BaseExpand(base):
    """BaseExpand(base) -> string.

    given a degenerated base, returns its meaning in IUPAC alphabet.

    i.e:
        b= 'A' -> 'A'
        b= 'N' -> 'ACGT'
        etc..."""
    base = base.upper()
    return dna_alphabet[base]

#function to convert recog site into regex, from Biopython
def regex(site):
    """regex(site) -> string.

    Construct a regular expression from a DNA sequence.
    i.e.:
        site = 'ABCGN'   -> 'A[CGT]CG.'"""
    reg_ex = site
    for base in reg_ex:
        if base in ('A', 'T', 'C', 'G', 'a', 'c', 'g', 't'):
            pass
        if base in ('N', 'n'):
            reg_ex = '.'.join(reg_ex.split('N'))
            reg_ex = '.'.join(reg_ex.split('n'))
        if base in ('R', 'Y', 'W', 'M', 'S', 'K', 'H', 'D', 'B', 'V'):
            expand = '['+ str(BaseExpand(base))+']'
            reg_ex = expand.join(reg_ex.split(base))
    return reg_ex

def ToRegex(site, name):
	sense = ''.join(['(?P<', name, '>', regex(site.upper()), ')'])
	antisense = ''.join(['(?P<', name, '_as>', regex(revcomp( site.upper() )), ')'])
	rg = sense + '|' + antisense
	return rg	

class restrictionEnzyme(object):
	def __init__(self,name="", buffer1="", buffer2="", buffer3="", buffer4="", bufferecori="", heatinact="", incubatetemp="", recognitionsite="",distance=""):
		self.name = name
		self.buffer_activity =[buffer1, buffer2, buffer3, buffer4, bufferecori]
		self.inactivate_temp = heatinact
		self.incubate_temp = incubatetemp
		#human-readable recognition site
		self.recognition_site = recognitionsite
		self.endDistance = distance
		#function to convert recog site into regex
		alpha_only_site = re.sub('[^a-zA-Z]+', '', recognitionsite)
		self.alpha_only_site = alpha_only_site
		# print ToRegex(alpha_only_site, name)
		self.compsite = ToRegex(alpha_only_site, name)
		#convert information about where the restriction happens to an offset on the top and bottom strand
		#for example, BamHI -> 1/5 with respect to the start of the site match
		hasNum = re.compile('-?\d+/-?\d+')
		not_completed = 1
		for m in hasNum.finditer(recognitionsite):
			(top, bottom) = m.group().split('/')
		  	self.top_strand_offset = int(top)
		  	self.bottom_strand_offset = int(bottom)
		  	not_completed = 0
		p = re.compile("/")
		for m in p.finditer(recognitionsite):
			if not_completed:
				self.top_strand_offset = int(m.start())
				self.bottom_strand_offset = len(recognitionsite) - 1 - self.top_strand_offset	

	def prettyPrint(self):
		print "Name: ", self.name, "Recognition Site: ", self.recognition_site
	def find_sites(self, DNA):
		seq = DNA.sequence
		(fwd, rev) = self.compsite.split('|')
		fwd_rease_re = re.compile(fwd)
		rev_rease_re = re.compile(rev)
		indices = []
		seen = {}
		if DNA.topology == "circular":
			searchSequence = seq.upper() + seq[0:len(self.recognition_site)-2]
		else:
			searchSequence = seq.upper()
		for m in fwd_rease_re.finditer(searchSequence):
			span = m.span()
			span = (span[0] % len(seq), span[1] % len(seq))
			seen[span[0]] = 1
			span = span + ('sense',)
			indices.append(span)
		for m in rev_rease_re.finditer(searchSequence):
			span = m.span()
			try:
				seen[span[0]]
			except:
				span = span + ('antisense',)
				indices.append(span)	
		return indices

#accepts two primers and list of input template DNAs
def SOE(primer1, primer2, templates):
	return 0
#accepts DNA, list of enzyme names, outputs list of DNA fragments, or uncut DNA
#may change enzymes into objects to get rid of need to always type ""
def Digest(inputDNA, enzymes):
    #there needs to be an enzyme class... we'll want to invoke that when dealing with heat inactivations
	#NEBEnzymes.tsv     name  buffers 1, 2, 3, 4, ecori, heat inact, incubation temp, recognition site, cleavage from end
	#find where the enzyme recognition site is with regex re.compile(compsite)
	#generate the appropriate n+1 or n linear molecules resulting from the digest
	return 0

def Distinguish2DNABands(a, b):
        #case of 2
	#for a standard 1-2% agarose gel,
        #we can distinguish a and b if
        return ( abs(a.length - b.length) > (0.208*a.length+42))  & (min(a.length, b.length) > 250 )

def DistinguishDNABands(list_of_dnas):
	ret_val = True
	for i in range(len(list_of_dnas)-1):
		ret_val = ret_val & Distinguish2DNABands(list_of_dnas[i], list_of_dnas[i+1])
	return ret_val

def FindDistinguishingEnzyme(list_of_dnas):
	#find the REase that can distinguish between the input DNAs
	#DistinguishDNABands(a, b) returns true if we can
	# tell apart bands a, b on a gel and a and b are both > 300bp, < 7kb
	#Let n be the number of DNAs in the list.  Let E be the enzyme under question
	# Then we construct a n-dimensional matrix
	# where the dimensions have max value defined by the number of fragments generated by E
	# E can be used to distinguish between the DNAs if there is a complete row or column 
	# that is distinguishable (all True by DistinguishDNABands)
	
	#iterate over all enzymes (enzyme list should be prioritized by availability and "goodness")
		#execute find good enz
	#iterate over all combinations of 2 enzymes
		#execute find good enz

	##find good enz
	#for each enzyme/combo in the list
		#calculate fragments for each input DNA
		#skip if any DNA has # fragments > 6
		#n-length list, each character represents the DNA fragment currently under investigation
		#iterate to fill in the hypermatrix values

		#find if the hypermatrix has a column/row that has all True
	return 0
def FindDistEnz():
	return FindDistinguishingEnzyme(list_of_dnas)

#accepts list of DNA, outputs list of DNA
def Ligate(inputDNAs):
	return 0
#accepts list of dnas and a strain, unsure what it outputs...
def Transform(DNAs, strain):
	return 0


#####Origins#####
def HasColE2(seq):
	#has ColE2 origin, data from PMID 16428404
	#'nnnntga[gt]ac[ct]agataagcc[tgc]tatcagataacagcgcccttttggcgtctttttgagcacc' 
	#necessary and sufficient element for ColE2 replication, however a longer sequence is needed for stable replication
	# 'AGCGCCTCAGCGCGCCGTAGCGTCGATAAAAATTACGGGCTGGGGCGAAACTACCATCTGTTCGAAAAGGTCCGTAAATGGGCCTACAGAGCGATTCGTCAGGGCTGGCCTGTATTCTCACAATGGCTTGATGCCGTTATCCAGCGTGTCGAAATGTACAACGCTTCGCTTCCCGTTCCGCTTTCTCCGGCTGAATGTCGGGCTATTGGCAAGAGCATTGCGAAATATACACACAGGAAATTCTCACCAGAGGGATTTTCCGCTGTACAGGCCGCTCGCGGTCGCAAGGGCGGAACTAAATCTAAGCGCGCAGCAGTTCCTACATCAGCACGTTCGCTGAAACCGTGGGAGGCATTAGGCATCAGTCGAGCGACGTACTACCGAAAATTAAAATGTGACCCAGACCTCGCnnnntga'
	#longer element shown in the Anderson lab that stably replicates
	return 0

def HasR6K(seq):
	#has R6k, data from Anderson lab observations
	#'aGCAGTTCAACCTGTTGATAGtacgtactaagctctcatgtttcacgtactaagctctcatgtttaacgtactaagctctcatgtttaacgaactaaaccctcatggctaacgtactaagctctcatggctaacgtactaagctctcatgtttcacgtactaagctctcatgtttgaacaataaaattaatataaatcagcaacttaaatagcctctaaggttttaagttttataagaaaaaaaagaatatataaggcttttaaagcttttaaggtttaacggttgtggacaacaagccagggatgtaacgcactgagaagcccttagagcctctcaaagcaattttgagtgacacaggaacacttaacggctgacatgggaattagccatgggcccgtgcgaatcac'
	return 0

def HasP15A(seq):
	return 0



###Tester#####
pbca1256 = DNA("ATGGTGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAATATATATATATATATATATATATATATAATATATATATATATATATATATGCTAGCGGCAGTGGATCTAGTGAATTTTCCCAGACAGTCCCCGAACTGGTTGCCTGGGCCAGAAAAAATGACTTCTCCATCTCGCTGCCGGTAGACCGACTCTCTAGGCTGCTGGCGGTTGCCACGCTGAACGGCGAGCGTCTGGATGGTGAGATGAGTGAAGGCGAGCCCGTGGATGCAGTGCGCCATGGGAGTGATGGTACCGCCTCCTCGGATCCACTGGCCGTCGTTTTACACCTAGGTGCTCAAAAAGACGCCAAAAGGGCGCTGTTATCTGATAAGGCTTATCTGGTATCATTTTGCGAGGTCTGGGTCACATTTTAATTTTCGGTAGTACGTCGCTCGACTGATGCCTAATGCCTCCCACGGTTTCAGCGAACGAGATGAGTGAAGGCGAGCTGGTGGATGCATTCCGCCATGTGAGTGATGCGTTTGAGCAAACCAGCGAAACCATCGGCGTGCGCGCCAATAACGCGATCAACGACATGGTGCGTCAACGTCTGCTGAACCGCTTTACCAGCGAGCAGGCGGAAGGGAACGCAATTTACCGTCTGACGCCGCTCGGCATCGGCATTACTGACTACNNNATCCGTCAGCGCGAGTTTTCTACGCTGCGTCTTTCTATGCAGTTGTCGATTGTGGCGGGTGAGCTCAAACGCGCAGCAGATGCCGCCGAAGAGGGCGGTGATGAATTTCACTGGCACCGTAATGTCTATGCGCCACTGAAATATTCGGTAGCAGAAATTTTCGACAGTATCGACCTGACGCAACGTCTGATGGACGAACAGCAGCAGCAGGTGAAGGACGATATCGCCCAGTTGCTGAACAAAGACTGGCGGGCGGCGATTTCCAGCTGTGAATTGTTGCTTTCGGAAACTTCCGGAACGCTGCGTGAATTGCAGGATACGCTGGAAGCGGCAGGCGACAAATTGCAGGCTAATCTGTTGCGCATTCAGGATGCGACGATGACCCATGACGATCTGCATTTCGTCGATCGTCTGGTGTTCGATCTGCAGAGCAAACTCGATCGTATTATCAGTTGGGGCCAGCAATCCATCGACTTGTGGATTGGCTACGACCGCCACGTACACAAATTTATTCGTACCGCGATCGATATGGATAAAAACCGCGTCTTTGCTCAGCGGTTACGTCAGTCGGTACAAACCTATTTTGATGAGCCGTGGGCGCTAACTTATGCCAATGCCGATCGTCTGCTGGATATGCGTGACGAAGAGATGGCACTCTTGGTCTGGTGGTACGCGAATATCTGTCACAGTATCCGCGTGCACGTCACTTTGACGTTGCGCGTATTGTTATTGATC","plasmid")
otherstuff = DNA("TTCGCTAAGGATCTGAAGTGGAATTCATGAGATCTTTATAGCTTGCTCAGTCCTAGGTACAATGCTTGCTACTAGTAGACATAAAAACGGCAAAGTATGAGCACAAAAAAGAAACCATTAACACAAGAGCAGCTTGAGGACGCACGTCGCCTTAAAGCAATTTATGAAAAAAAGAAAAATGAACTTGGCTTATCCCAGGAATCTGTCGCAGACAAGATGGGGATGGGGCAGTCAGGCGTTGGTGCTTTATTTAATGGCATCAATGCATTAAATGCTTATAACGCCGCATTGCTTGCAAAAATTCTCAAAGTTAGCGTTGAAGAATTTAGCCCTTCAATCGCCAGAGAAATCTACGAGATGTATGAAGCGGTTAGTATGCAGCCGTCACTTAGAAGTGAGTATGAGTACCCTGTTTTTTCTCATGTTCAGGCAGGGATGTTCTCACCTGAGCTTAGAACCTTTACCAAAGGTGATGCGGAGAGATGGGTAAGCACAGCTAGCGGCAGTGGATCTAGTGAATTTTCCCAGACAGTCCCCGAACTGGTTGCCTGGGCCAGAAAAAATGACTTCTCCATCTCGCTGCCGGTAGACCGACTCTCTAGGCTGCTGGCGGTTGCCACGCTGAACGGCGAGCGTCTGGATGGTGAGATGAGTGAAGGCGAGCCCGTGGATGCAGTGCGCCATGGGAGTGATGGTACCGCCTCCTCGGATCCACTGGCCGTCGTTTTACACCTAGGTGCTCAAAAAGACGCCAAAAGGGCGCTGTTATCTGATAAGGCTTATCTGGTATCATTTTGCGAGGTCTGGGTCACATTTTAATTTTCGGTAGTACGTCGCTCGACTGATGCCTAATGCCTCCCACGGTTTCAGCGAACGTGCTGATGTAGGAACTGCTGCGCGCTTAGATTTAGTTCCGCCCTTGCGACCGCGAGCGGCCTGTACAGCGGAAAATCCCTCTGGTGAGAATTTCCTGTGTGTATATCGCAATGTCCCTGCGGGC", "plasmid")
other = DNA("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", "plasmid")
print pbca1256.length, otherstuff.length, other.length
print DistinguishDNABands([pbca1256, otherstuff])
#PCR("ATGAGTGAAGGCGAGCTGGTGGATG", "AATTTGTCGCCTGCCGCTTCCA",pbca1256)
#print synbioinformatica.PCR("ATGGTGAGATGAGTGAAGGCGAGCTGGTGGATGCATTCCGCCATGTGAGTGATGCGTTTGAGCAAACCAGCGAAACCATCGGCGTGCGCGCCAATAACGCGATCAACGACATGGTGCGTCAACGTCTGCTGAACCGCTTTACCAGCGAGCAGGCGGAAGGGAACGCAATTTACCGTCTGACGCCGCTCGGCATCGGCATTACTGACTACNNNATCCGTCAGCGCGAGTTTTCTACGCTGCGTCTTTCTATGCAGTTGTCGATTGTGGCGGGTGAGCTCAAACGCGCAGCAGATGCCGCCGAAGAGGGCGGTGATGAATTTCACTGGCACCGTAATGTCTATGCGCCACTGAAATATTCGGTAGCAGAAATTTTCGACAGTATCGACCTGACGCAACGTCTGATGGACGAACAGCAGCAGCAGGTGAAGGACGATATCGCCCAGTTGCTGAACAAAGACTGGCGGGCGGCGATTTCCAGCTGTGAATTGTTGCTTTCGGAAACTTCCGGAACGCTGCGTGAATTGCAGGATACGCTGGAAGCGGCAGGCGACAAATTGCAGGCTAATCTGTTGCGCATTCAGGATGCGACGATGACCCATGACGATCTGCATTTCGTCGATCGTCTGGTGTTCGATCTGCAGAGCAAACTCGATCGTATTATCAGTTGGGGCCAGCAATCCATCGACTTGTGGATTGGCTACGACCGCCACGTACACAAATTTATTCGTACCGCGATCGATATGGATAAAAACCGCGTCTTTGCTCAGCGGTTACGTCAGTCGGTACAAACCTATTTTGATGAGCCGTGGGCGCTAACTTATGCCAATGCCGATCGTCTGCTGGATATGCGTGACGAAGAGATGGCACTGCGCGATGAAGAAGTGACTGGGGAACTTCCTGAGGATCTGGAATACGAAGAGTTTAACGAGATCCGCGAACAGCTGGCGGCGATCATCGAAGAACAACTTGCCGTGTACAAAACCAGACAAGTGCCGCTGGATCTTGGTCTGGTGGTACGCGAATATCTGTCACAGTATCCGCGTGCACGTCACTTTGACGTTGCGCGTATTGTTATTGATC", "ATGAGTGAAGGCGAGCTGGTGGATG", "AATTTGTCGCCTGCCGCTTCCA")
