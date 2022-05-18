import random

class FOTStreet:
	def __init__(self) -> None:
		self.l_fake_street = [
			'Rue de l\'Hirondelle',
			'Rue Etienne Compayre',
			'Rue Porte Peyrole',
			'Petite Rue du Patis',
			'Rue des Remparts',
			'Rue de la Biade',
			'Rue des Fleurs']

		self.save = list(self.l_fake_street)

	def run(self, _):
		t = self.l_fake_street[ random.randint(0, len(self.l_fake_street) - 1) ]
		return t

if __name__ == "__main__":
	for _ in range(5): print(FOTStreet().run('OUi'))