class Encoder:
	def name(self):
		raise NotImplementedError

	def encode(self, obj):
		raise NotImplementedError

	def decode(self):
		raise NotImplementedError

	def shape(self):
		raise NotImplementedError

