from scanner.risk import position_size

def test_position_size():
    qty, risk = position_size(100, 97, 300)
    assert qty == 100
    assert risk == 300
