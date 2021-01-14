import pickle
import shutil
import pathlib
import cv2 as cv
import numpy as np

def get_centroid(image):
    thresh = cv.threshold(image, 127, 255, 0)[1]
    M = cv.moments(thresh)
    c_x = int(M['m10'] / M['m00'])
    c_y = int(M['m01'] / M['m00'])
    
    return (c_x, c_y)

def get_weights(centroid, area):    
    dists = [np.sqrt((pnt[0] - centroid[0])**2 + (pnt[1] - centroid[1])**2) for pnt in area]
    #print(dists)
    scale = max(dists) / 3 # Makes outer points ~20x less likely as centroid
    dists_exp = [np.exp(-dist / scale) for dist in dists]
    sum_dists = sum(dists_exp)
    dists_normed = [dist/sum_dists for dist in dists_exp]
    
    return dists_normed

def get_distribution(image, centroid=None):
    area = np.where(image == 255)
    area = list(zip(area[1], area[0]))
    centroid = get_centroid(image) if centroid is None else centroid
    distribution = get_weights(centroid, area)
    
    mask = np.zeros_like(image)
    conv = 255 / max(distribution)
    for i in range(len(distribution)):
        mask[area[i][1]][area[i][0]] = conv * distribution[i]
    
    image.fill(0)
    return image, mask, (area, distribution)

def create_distributions():
    shutil.rmtree('Areas', ignore_errors=True)
    pathlib.Path('Areas').mkdir(parents=True, exist_ok=True)
    pathlib.Path('Areas/images').mkdir(parents=True, exist_ok=True)
    
    print('Creating Click Distributions in \'Areas\' folder...')
    distributions = {}
    
    empty = np.zeros((1080, 1920), np.uint8)
    
    minion_centers = [
        [
            [
                (961, 591)
            ],
            [
                (892, 591), (1030, 591)
            ],
            [
                (823, 591), (961, 591), (1099, 591)
            ],
            [
                (754, 591), (892, 591), (1030, 591), (1168, 591)
            ],
            [
                (685, 591), (823, 591), (961, 591), (1099, 591), (1237, 591)
            ],
            [
                (616, 591), (754, 591), (892, 591), (1030, 591), (1168, 591), (1306, 591)
            ],
            [
                (547, 591), (685, 591), (823, 591), (961, 591), (1099, 591), (1237, 591), (1375, 591)
            ]
        ],
        [
            [
                (961, 406)
            ],
            [
                (892, 406), (1030, 406)
            ],
            [
                (823, 406), (961, 406), (1099, 406)
            ],
            [
                (754, 406), (892, 406), (1030, 406), (1168, 406)
            ],
            [
                (685, 406), (823, 406), (961, 406), (1099, 406), (1237, 406)
            ],
            [
                (616, 406), (754, 406), (892, 406), (1030, 406), (1168, 406), (1306, 406)
            ],
            [
                (547, 406), (685, 406), (823, 406), (961, 406), (1099, 406), (1237, 406), (1375, 406)
            ]
        ]
    ]
    
    hand_polygons = [
        [
            [(860, 940), (983, 940), (983, 1080), (860, 1080)]
        ],
        [
            [(794, 940), (916, 940), (916, 1080), (794, 1080)],
            [(927, 940), (1049, 940), (1049, 1080), (927, 1080)]
        ],
        [
            [(728, 940), (851, 940), (851, 1080), (728, 1080)],
            [(860, 940), (983, 940), (983, 1080), (860, 1080)],
            [(992, 940), (1115, 940), (1115, 1080), (992, 1080)]
        ],
        [
            [(642, 983), (685, 1080), (800, 1080), (793, 1018), (754, 932)],
            [(787, 951), (803, 1080), (913, 1080), (920, 1023), (908, 934)],
            [(936, 942), (916, 1080), (1031, 1080), (1044, 1051), (1055, 958)],
            [(1088, 958), (1035, 1080), (1168, 1080), (1198, 1005)]
        ],
        [
            [(629, 983), (671, 1080), (765, 1080), (743, 976), (735, 969), (740, 931)],
            [(745, 957), (770, 1080), (856, 1080), (856, 959), (850, 951), (860, 930)],
            [(861, 941), (861, 1080), (947, 1080), (973, 965), (970, 954), (980, 940)],
            [(982, 947), (953, 1080), (1045, 1080), (1092, 980), (1091, 969)],
            [(1104, 966), (1051, 1080), (1183, 1080), (1211, 1015)]
        ],
        [
            [(619, 995), (659, 1080), (740, 1080), (715, 986), (707, 979), (713, 949)],
            [(714, 966), (744, 1080), (817, 1080), (809, 968), (802, 958), (809, 939)],
            [(812, 947), (822, 1080), (893, 1080), (904, 957), (900, 948), (906, 936)],
            [(910, 941), (898, 1080), (969, 1080), (1002, 960), (1000, 950), (1004, 945)],
            [(1011, 945), (974, 1080), (1050, 1080), (1101, 977), (1100, 965)],
            [(1114, 959), (1055, 1080), (1188, 1080), (1220, 1010)]
        ],
        [
            [(613, 995), (655, 1080), (723, 1080), (696, 990), (687, 982), (692, 954)],
            [(695, 969), (728, 1080), (791, 1080), (775, 972), (767, 964), (774, 943)],
            [(777, 952), (796, 1080), (856, 1080), (856, 959), (850, 951), (857, 938)],
            [(861, 942), (861, 1080), (921, 1080), (939, 960), (936, 951), (943, 939)],
            [(947, 944), (926, 1080), (988, 1080), (1024, 968), (1022, 958), (1025, 953)],
            [(1034, 953), (993, 1080), (1060, 1080), (1110, 981), (1109, 974)],
            [(1122, 970), (1066, 1080), (1200, 1080), (1227, 1021)]
        ],
        [
            [(606, 1007), (644, 1080), (708, 1080), (681, 1000), (672, 994), (673, 971)],
            [(679, 981), (713, 1080), (770, 1080), (750, 981), (742, 972), (745, 956)],
            [(751, 960), (774, 1080), (828, 1080), (821, 965), (815, 956), (819, 944)],
            [(824, 944), (832, 1080), (884, 1080), (892, 958), (888, 948), (892, 939)],
            [(897, 940), (888, 1080), (940, 1080), (966, 957), (963, 947), (968, 941)],
            [(974, 941), (944, 1080), (999, 1080), (1041, 963), (1039, 953)],
            [(1050, 949), (1003, 1080), (1062, 1080), (1117, 976), (1116, 970)],
            [(1128, 962), (1066, 1080), (1202, 1080), (1233, 1018)]
        ],
        [
            [(602, 1005), (642, 1080), (699, 1080), (669, 1001), (660, 996), (662, 973)],
            [(665, 980), (703, 1080), (754, 1080), (730, 983), (722, 976), (725, 957)],
            [(729, 963), (758, 1080), (806, 1080), (793, 969), (786, 960), (790, 947)],
            [(794, 949), (810, 1080), (857, 1080), (857, 960), (851, 950), (855, 940)],
            [(860, 940), (860, 1080), (906, 1080), (921, 958), (917, 949), (923, 939)],
            [(927, 941), (910, 1080), (957, 1080), (987, 963), (984, 953), (988, 947)],
            [(995, 947), (961, 1080), (1012, 1080), (1053, 974), (1052, 963), (1055, 960)],
            [(1064, 957), (1015, 1080), (1071, 1080), (1121, 986), (1121, 978)],
            [(1133, 973), (1075, 1080), (1211, 1080), (1237, 1030)]
        ],
        [
            [(598, 1019), (632, 1080), (687, 1080), (659, 1014), (650, 1007), (651, 988)],
            [(655, 994), (691, 1080), (739, 1080), (714, 993), (706, 986), (708, 971)],
            [(713, 973), (744, 1080), (787, 1080), (771, 976), (764, 968), (767, 956)],
            [(771, 957), (792, 1080), (834, 1080), (828, 965), (822, 956), (825, 946)],
            [(831, 943), (838, 1080), (879, 1080), (886, 958), (881, 948), (884, 940)],
            [(890, 940), (882, 1080), (923, 1080), (944, 957), (941, 947), (945, 940)],
            [(951, 939), (927, 1080), (969, 1080), (1004, 960), (1002, 951), (1004, 946)],
            [(1013, 943), (973, 1080), (1018, 1080), (1065, 969), (1064, 956)],
            [(1075, 952), (1022, 1080), (1070, 1080), (1126, 981), (1126, 973)],
            [(1137, 967), (1074, 1080), (1212, 1080), (1241, 1027)]
        ]
    ]
    
    choose_rects = [
        [
            ((824, 345), (1086, 717))
        ],
        [
            ((663, 351), (911, 716)),
            ((1014, 351), (1262, 716))
        ],
        [
            ((440, 344), (695, 718)),
            ((828, 344), (1083, 718)),
            ((1216, 344), (1471, 718))
        ],
        [
            ((273, 349), (526, 715)),
            ((644, 349), (897, 715)),
            ((1015, 349), (1268, 715)),
            ((1386, 349), (1639, 715))
        ]
    ]
    
    mulligan_rects = [
        [
            ((520, 365), (722, 663)),
            ((862, 365), (1064, 663)),
            ((1204, 365), (1406, 663))
        ],
        [
            ((480, 365), (682, 663)),
            ((736, 365), (938, 663)),
            ((992, 365), (1194, 663)),
            ((1248, 365), (1450, 663))
        ]
    ]
    
    hero_polygons = [
        [(962, 736), (912, 763), (890, 809), (890, 904), (1034, 904), (1034, 809), (1012, 763)],
        [(962, 111), (913, 138), (891, 184), (891, 274), (1033, 274), (1033, 184), (1011, 138)]
    ]
    
    minions = []
    board_mask = np.zeros((1080, 1920), np.uint8)
    for minion_center_side in minion_centers:
        minions_side = []
        for minion_count in minion_center_side:
            minions_current = []
            for minion_center in minion_count:
                cv.ellipse(empty, minion_center, (59, 80), 0, 0, 360, 255, -1)
                empty, mask, dist = get_distribution(empty, (minion_center[0] + 4, minion_center[1] - 5))
                board_mask = cv.bitwise_or(board_mask, mask)
                minions_current.append(dist)
            minions_side.append(minions_current)
            cv.imwrite('Areas/images/board_' + str(int(minion_center_side[0][0][1] == 406)) + '_' + str(len(minions_current)) + '.png', board_mask)
            board_mask.fill(0)
        minions.append(minions_side)
    distributions.update({'minions': minions})
    print('Completed minion distributions.')
        
    hand = []
    hand_mask = np.zeros((1080, 1920), np.uint8)
    for hand_polygon in hand_polygons:
        hand_current = []
        for card in hand_polygon:
            vertices = np.array([card], np.int32)
            cv.fillPoly(empty, [vertices], 255)
            empty, mask, dist = get_distribution(empty)
            hand_mask = cv.bitwise_or(hand_mask, mask)
            hand_current.append(dist)
        hand.append(hand_current)
        cv.imwrite('Areas/images/hand_' + str(len(hand_polygon)) + '.png', hand_mask)
        hand_mask.fill(0)
    distributions.update({'hand': hand})
    print('Completed hand distributions.')
        
    choose = []
    choose_mask = np.zeros((1080, 1920), np.uint8)
    for choose_rect in choose_rects:
        choose_current = []
        for card in choose_rect:
            cv.rectangle(empty, card[0], card[1], 255, -1)
            empty, mask , dist = get_distribution(empty)
            choose_mask = cv.bitwise_or(choose_mask, mask)
            choose_current.append(dist)
        choose.append(choose_current)
        cv.imwrite('Areas/images/choose_' + str(len(choose_rect)) + '.png', choose_mask)
        choose_mask.fill(0)
    distributions.update({'choose': choose})
    print('Completed choose distributions.')
    
    mulligan = []
    mulligan_mask = np.zeros((1080, 1920), np.uint8)
    for mulligan_rect in mulligan_rects:
        mulligan_current = []
        for card in mulligan_rect:
            cv.rectangle(empty, card[0], card[1], 255, -1)
            empty, mask, dist = get_distribution(empty)
            mulligan_mask = cv.bitwise_or(mulligan_mask, mask)
            mulligan_current.append(dist)
        mulligan.append(mulligan_current)
        cv.imwrite('Areas/images/mulligan_' + str(len(mulligan_rect)) + '.png', mulligan_mask)
        mulligan_mask.fill(0)
    distributions.update({'mulligan': mulligan})
    print('Completed mulligan distributions.')
    
    cv.rectangle(empty, (648, 263), (1506, 777), 255, -1)
    empty, mask, dist = get_distribution(empty, (1220, 500))
    distributions.update({'play': dist})
    cv.imwrite('Areas/images/play.png', mask)
    print('Completed play distribution.')
    
    heros = []
    hero_mask = np.zeros((1080, 1920), np.uint8)
    for hero_polygon in hero_polygons:
        vertices = np.array([hero_polygon], np.int32)
        cv.fillPoly(empty, [vertices], 255)
        empty, mask, dist = get_distribution(empty)
        hero_mask = cv.bitwise_or(hero_mask, mask)
        heros.append(dist)
    distributions.update({'heros': heros})
    cv.imwrite('Areas/images/heros.png', hero_mask)
    print('Completed hero distributions.')
    
    cv.circle(empty, (1141, 831), 76, 255, -1)
    empty, mask, dist = get_distribution(empty)
    distributions.update({'hero_power': dist})
    cv.imwrite('Areas/images/hero_power.png', mask)
    print('Completed hero power distribution.')
    
    cv.rectangle(empty, (1500, 476), (1622, 509), 255, -1)
    cv.ellipse(empty, (1561, 476), (61, 11), 180, 0, 180, 255, -1)
    cv.ellipse(empty, (1561, 509), (61, 11), 0, 0, 180, 255, -1)
    empty, mask, dist = get_distribution(empty)
    distributions.update({'end_turn': dist})
    cv.imwrite('Areas/images/end_turn.png', mask)
    print('Completed end turn distribution.')
    
    cv.circle(empty, (1401, 889), 86, 255, -1)
    empty, mask, dist = get_distribution(empty)
    distributions.update({'start_game': dist})
    cv.imwrite('Areas/images/start_game.png', mask)
    print('Completed start game distribution.')
    
    cv.rectangle(empty, (893, 835), (1035, 873), 255, -1)
    cv.ellipse(empty, (964, 835), (71, 13), 180, 0, 180, 255, -1)
    cv.ellipse(empty, (964, 873), (71, 13), 0, 0, 180, 255, -1)
    empty, mask, dist = get_distribution(empty)
    distributions.update({'confirm_mulligan': dist})
    cv.imwrite('Areas/images/confirm_mulligan.png', mask)
    print('Completed confirm mulligan distribution.')
    
    cv.rectangle(empty, (650, 236), (1340, 1040), 255, -1)
    empty, mask, dist = get_distribution(empty)
    distributions.update({'end_game': dist})
    cv.imwrite('Areas/images/end_game.png', mask)
    print('Completed end game distribution.')
    
    cv.rectangle(empty, (875, 365), (1047, 403), 255, -1)
    empty, mask, dist = get_distribution(empty)
    distributions.update({'concede': dist})
    cv.imwrite('Areas/images/concede.png', mask)
    print('Completed concede distribution.')
    
    cv.rectangle(empty, (1857, 1040), (1897, 1070), 255, -1)
    empty, mask, dist = get_distribution(empty)
    distributions.update({'settings': dist})
    cv.imwrite('Areas/images/settings.png', mask)
    print('Completed settings distribution.')
    
    print('Saving distributions...')
    with open('Areas/distributions.txt', 'wb') as f:
        pickle.dump(distributions, f)
    print('Finished writing distribution file and images.')

if __name__ == '__main__':
    create_distributions()