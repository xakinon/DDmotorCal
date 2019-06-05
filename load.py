class LoadCheck():

    def __init__(self, dd_motor, work, load, condition):
        self.dd_motor = dd_motor
        self.work = work
        self.load = load
        self.condition = condition

    def max_moment(self):
        moment_work = self.work['force'] * (self.work['offset'] + self.dd_motor['ベアリングオフセット'])
        moment_load = self.load['force'] * self.load['offset']
        return moment_work + moment_load

    def radial_force_average(self):
        return self.work['force']
        
    def axial_force_average(self):
        return self.load['force']
        
    def load_factor(self):
        mr = self.radial_force_average() * (self.work['offset'] + self.dd_motor['ベアリングオフセット'])
        ma = self.axial_force_average() * self.load['offset']
        k = self.axial_force_average() / (self.radial_force_average() + 2*(mr + ma) / self.dd_motor['ベアリングピッチ円直径'] )
        if k <= 1.5:
            return 1, 0.45, k
        return 0.67, 0.67, k

    def dynamic_equivalent_radial_load(self):
        x, y, k = self.load_factor()
        mr = self.radial_force_average() * (self.work['offset'] + self.dd_motor['ベアリングオフセット'])
        ma = self.axial_force_average() * self.load['offset']
        pc = x * (self.radial_force_average() + 2*(mr + ma) / self.dd_motor['ベアリングピッチ円直径'] ) + y * self.axial_force_average()
        return pc

    def life_time(self):
        a1 = 10 ** 6 / (60 * self.condition['revolution_average'])
        a2 = (self.dd_motor['基本動定格荷重']/(self.load['load_factor']*self.dynamic_equivalent_radial_load())) ** (10/3)
        return a1 * a2

    def life_time_roking(self):
        a1 = 10 ** 6 / (60 * self.condition['rocking_times'])
        a2 = 90 / self.condition['rocking_angle']
        a3 = (self.dd_motor['基本動定格荷重']/(self.load['load_factor']*self.dynamic_equivalent_radial_load())) ** (10/3)
        return a1 * a2 * a3

    def static_equivalent_radial_load(self):
        po = self.work['force'] + 2 * self.max_moment() / self.dd_motor['ベアリングピッチ円直径'] + 0.44 * self.load['force']
        return po

    def static_safety_factor(self):
        fs = self.dd_motor['基本静定格荷重'] / self.static_equivalent_radial_load()
        return fs

def read_csv(file):
    def toFloat(str_):
        try:
            return float(str_)
        except ValueError:
            return str_
    def toDict(row):
        return { key:toFloat(row[key]) for key in row }
    
    import csv
    with open(file, encoding='shift_jis') as f:
        dr = list( csv.DictReader(f) )
        ls = [ toDict(row) for row in dr ]
    return ls

def write_csv(file, dicts):
    import csv
    with open(file, 'w') as f:
        dw = csv.DictWriter(f, fieldnames=dicts[0].keys(), lineterminator='\n')
        dw.writeheader()
        dw.writerows(dicts)

if __name__ == '__main__':
    
    dd_motors = read_csv('dd_motor.csv')
    condition = { 'rocking_times':60, 'rocking_angle':15, 'revolution_average':60 }
    work = {'force':0.662 * 9.8, 'offset':11.856}
    load = {'force':0.662 * 10, 'offset':0.000000969, 'load_factor':1.5}

    results = []
    for dd_motor in dd_motors[1:]:

        loadCheck = LoadCheck(dd_motor, work, load, condition)

        result = {}
        result[ '型式' ] = dd_motor['型式']
        result[ '最大モーメント' ] = loadCheck.max_moment()
        result[ '平均ラジアル荷重' ] = loadCheck.radial_force_average()
        result[ '平均アキシャル荷重' ] = loadCheck.axial_force_average()
        result[ '荷重係数' ] = loadCheck.load_factor()
        result[ '動等価ラジアル荷重' ] = loadCheck.dynamic_equivalent_radial_load()
        result[ '寿命時間' ] = loadCheck.life_time()
        result[ '寿命日数' ] = loadCheck.life_time() / 24
        result[ '寿命年数' ] = loadCheck.life_time() / 24 / 365
        result[ '揺動寿命時間' ] = loadCheck.life_time_roking()
        result[ '揺動寿命日数' ] = loadCheck.life_time_roking() / 24
        result[ '揺動寿命年数' ] = loadCheck.life_time_roking() / 24 / 365
        result[ '静等価ラジアル荷重' ] = loadCheck.static_equivalent_radial_load()
        result[ '静安全係数' ] = loadCheck.static_safety_factor()
        results.append(result)

    write_csv('results.csv', results)
