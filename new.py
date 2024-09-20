class Solution(object):
    def romanToInt(self, s):
        oldA = 0
        newA = 0
        x = 0
        for a in s:
            if a == 'I':
                newA = 1
            elif a == 'V':
                newA = 5
            elif a == 'X':
                newA = 10
            elif a == 'L':
                newA = 50
            elif a == 'C':
                newA = 100
            elif a == 'D':
                newA = 500
            elif a == 'M':
                newA = 1000
            if oldA < newA:
                x -= oldA
            else:
                x += oldA
            oldA = newA
        x += newA
        return x


a = Solution()
print(a.romanToInt('MCMXCIV'))
