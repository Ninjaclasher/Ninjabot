import settings

def edit_dist(a, b):
    dp = [[0 for x in range(len(b)+1)] for y in range(2)]
    for x in range(len(a)+1):
        for y in range(len(b)+1):
            if x == 0:
                dp[x&1][y] = y
            elif y == 0:
                dp[x&1][y] = x
            elif a[x-1] == b[y-1]:
                dp[x&1][y] = dp[x&1^1][y-1]
            else:
                dp[x&1][y] = 1 + min(dp[x&1][y-1], dp[x&1^1][y], dp[x&1^1][y-1])
    return dp[len(a)&1][-1]

def get_closest_user(server, content, include_bots=False):
    min_dis = 10**9
    user = None
    for x in server.members:
        if not x.bot or include_bots:
            names = [x.display_name.lower(), str(x).lower()]
            if x.id in settings.NAMES.keys():
                names.append(settings.NAMES[x.id])
            dis = min(edit_dist(content, x) for x in names)
            if dis < min_dis:
                min_dis, user = dis, x
            elif dis == min_dis:
                user = None
    return user
