class LoadCheck():

    def __init__(self, dd_motor, work, load):
        self.dd_motor = dd_motor
        self.work = work
        self.load = load

    def max_moment(self):
        moment_work = self.work['force'] * (self.work['offset'] + self.dd_motor['flange_offset'])
        moment_load = self.load['force'] * self.load['offset']
        return moment_work + moment_load

    def radial_force_average(self):
        return self.work['force']
        
    def axial_force_average(self):
        return self.load['force']
        
    def load_factor(self):
        mr = self.radial_force_average() * (self.work['offset'] + self.dd_motor['flange_offset'])
        ma = self.axial_force_average() * self.load['offset']
        a = self.axial_force_average() / (self.radial_force_average() + 2*(mr + ma) / self.dd_motor['roller_pitch_diameter'] )
        if a <= 1.5:
            return 1, 0.45
        return 0.67, 0.67

    def dynamic_equivalent_radial_load(self):
        x, y = self.load_factor()
        mr = self.radial_force_average() * (self.work['offset'] + self.dd_motor['flange_offset'])
        ma = self.axial_force_average() * self.load['offset']
        pc = x * (self.radial_force_average() + 2*(mr + ma) / self.dd_motor['roller_pitch_diameter'] ) + y * self.axial_force_average()
        return pc

    def life_time(self):
        a1 = 10 ** 6 / (60 * self.dd_motor['revolution_average'])
        a2 = (self.dd_motor['basic_load_rating']/(self.load['load_factor']*self.dynamic_equivalent_radial_load())) ** (10/3)
        return a1 * a2

    def static_equivalent_radial_load(self):
        po = self.work['force'] + 2 * self.max_moment() / self.dd_motor['roller_pitch_diameter'] + 0.44 * self.load['force']
        return po

    def static_safety_factor(self):
        fs = self.dd_motor['basic_static_load_rating'] / self.static_equivalent_radial_load()
        return fs

if __name__ == '__main__':
    dd_motor = {'flange_offset':12.9, 'roller_pitch_diameter':35, 'basic_static_load_rating':8000, 'basic_load_rating':5800, 'revolution_average':60}
    work = {'force':11, 'offset':20}
    load = {'force':11, 'offset':0, 'load_factor':1.5}

    loadCheck = LoadCheck(dd_motor, work, load)

    print( loadCheck.max_moment() )
    print( loadCheck.radial_force_average() )
    print( loadCheck.axial_force_average() )
    print( loadCheck.load_factor() )
    print( loadCheck.dynamic_equivalent_radial_load() )
    print( loadCheck.life_time() )
    print( loadCheck.static_equivalent_radial_load() )
    print( loadCheck.static_safety_factor() )