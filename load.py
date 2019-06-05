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
        k = self.axial_force_average() / (self.radial_force_average() + 2*(mr + ma) / self.dd_motor['roller_pitch_diameter'] )
        if k <= 1.5:
            return 1, 0.45, k
        return 0.67, 0.67, k

    def dynamic_equivalent_radial_load(self):
        x, y, k = self.load_factor()
        mr = self.radial_force_average() * (self.work['offset'] + self.dd_motor['flange_offset'])
        ma = self.axial_force_average() * self.load['offset']
        pc = x * (self.radial_force_average() + 2*(mr + ma) / self.dd_motor['roller_pitch_diameter'] ) + y * self.axial_force_average()
        return pc

    def life_time(self):
        a1 = 10 ** 6 / (60 * self.dd_motor['revolution_average'])
        a2 = (self.dd_motor['basic_load_rating']/(self.load['load_factor']*self.dynamic_equivalent_radial_load())) ** (10/3)
        return a1 * a2

    def life_time_roking(self):
        a1 = 10 ** 6 / (60 * self.dd_motor['rocking_times'])
        a2 = 90 / self.dd_motor['rocking_angle']
        a3 = (self.dd_motor['basic_load_rating']/(self.load['load_factor']*self.dynamic_equivalent_radial_load())) ** (10/3)
        return a1 * a2 * a3

    def static_equivalent_radial_load(self):
        po = self.work['force'] + 2 * self.max_moment() / self.dd_motor['roller_pitch_diameter'] + 0.44 * self.load['force']
        return po

    def static_safety_factor(self):
        fs = self.dd_motor['basic_static_load_rating'] / self.static_equivalent_radial_load()
        return fs

def write_csv(file, save_dicts):
    with open(file, 'w') as f:
        dw = csv.DictWriter(f, fieldnames=save_dicts[0].keys())
        dw.writeheader()
        dw.writerows(save_dicts)

if __name__ == '__main__':
    
    import csv

    with open('dd_motor.csv', encoding='shift_jis') as f:
        dr = list( csv.DictReader(f) )
        dd_motors = []
        for row in dr:
            dict_ = {}
            for key in row:
                try:
                    dict_[key] = float(row[key])
                except ValueError:
                    dict_[key] = row[key]
            dd_motors.append(dict_)
    

    work = {'force':0.662 * 9.8, 'offset':11.856}
    load = {'force':0.662 * 10, 'offset':0.000000969, 'load_factor':1.5}

    results = []
    for dd_motor in dd_motors:

        loadCheck = LoadCheck(dd_motor, work, load)

        result = {}
        result[ 'model_number' ] = dd_motor['model_number']
        result[ 'max_moment' ] = loadCheck.max_moment()
        result[ 'radial_force_average' ] = loadCheck.radial_force_average()
        result[ 'axial_force_average' ] = loadCheck.axial_force_average()
        result[ 'load_factor' ] = loadCheck.load_factor()
        result[ 'dynamic_equivalent_radial_load' ] = loadCheck.dynamic_equivalent_radial_load()
        result[ 'life_time_hour' ] = loadCheck.life_time()
        result[ 'life_time_day' ] = loadCheck.life_time() / 24
        result[ 'life_time_year' ] = loadCheck.life_time() / 24 / 365
        result[ 'life_time_roking_hour' ] = loadCheck.life_time_roking()
        result[ 'life_time_roking_day' ] = loadCheck.life_time_roking() / 24
        result[ 'life_time_roking_year' ] = loadCheck.life_time_roking() / 24 / 365
        result[ 'static_equivalent_radial_load' ] = loadCheck.static_equivalent_radial_load()
        result[ 'static_safety_factor' ] = loadCheck.static_safety_factor()

        results.append(result)

    write_csv('results.csv', results)
