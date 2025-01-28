def deploy_phase(p_one, p_two):
    p_one_passed = False
    p_two_passed = False
    p_one.set_phase("Deploy")
    p_two.set_phase("Deploy")
    if p_one.get_initiative():
        p_one.set_turn(True)
        p_two.set_turn(False)
    else:
        p_one.set_turn(False)
        p_two.set_turn(True)
    while not p_one_passed or not p_two_passed:
        if not p_one_passed:
            print(p_one_passed)
            p_one_passed = p_one.take_deploy_turn()
        if not p_two_passed:
            print(p_two_passed)
            p_two_passed = p_two.take_deploy_turn()
    print("Left deploy phase")
