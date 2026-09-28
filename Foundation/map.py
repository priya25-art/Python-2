# 1. Add 5 marks to every student
marks = [40,50,60,70,80,90]
result = list(map(lambda x:x+5, marks))
print(result)


# 2. Increase every price by 10%
prices = [100,200,300,400,500]
result = list(map(lambda x: x*1.10, prices))
print(result)


# 3. Find only even numbers from a list
numbers =[1,2,3,4,5,6,7,8,9,10]
result = list(filter(lambda x:x%2==0, numbers))
print(result)
even =[]
result = list(map(lambda x:even.append(x) if x%2==0 else even, numbers))
print(even)


def square(num):
    return num**2
print(square(5))


prices =[100,200,300]
discounted_prices = list(map(lambda x: x*0.9, prices))
print(discounted_prices)

marks =[40,50,60,70,80,90]
def marks_greater_than_50(marks):
    return list(filter(lambda x: x > 50, marks))
print(marks_greater_than_50(marks))

prices =[200,750,450,1000]
def prices_less_than_500(prices):
    return list(filter(lambda x: x < 500, prices))
print(prices_less_than_500(prices))