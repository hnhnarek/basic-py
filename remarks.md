

__1.__ Տողից նիշերի ցուցակ ստանալու համար կարելի է օգտագործել `list()` կոնստրուկտորը։
````python
>>> list('string')
['s', 't', 'r', 'i', 'n', 'g']
````

__2.__ Մի որևէ _բանալու_ (key) գոյությունը _բառարանում_ (dictionary) ստուգելու համար պետք է օգտագործել `in` գործողությունը։
````python
>>> d0 = {'x' : 1.2, 'z' : 3.4}
>>> 'x' in d0
True
>>> 'y' in d0
False
````

__3.__ `test0.txt` ֆայլի ամբողջ պարունակությունը կարդալու և `text` փոփոխականին վերագրելու համար կարելի է օգտագործել հետևյալ կառուցվածքը.
````python
text = ''
with open('test0.txt', 'r') as source:
    text = source.read()
````

__4.__ Իտերատոր իրականացնելու համար դասում պետք է սահմանել ու իրականացնել `__iter__` և `__next__` մեթոդները։ 

__5.__ Տողից իրական թիվ ստանալու համար պետք է օգտագործել `float()` ֆունկցիան։
````python
>>> float('3.14')
3.14
````

__6.__ Վարիադիկ ֆունկցիա սահմանելու համար պետք է ֆունկցիայի վերջին պարամետրի անունից առաջ գրել `*` նիշը։
````python
>>> def f(*args):
...     for e in args:
...         print(e)
>>> f(1)
1
>>> f(1,2,3)
1
2
3
````

__7.__ Մաթեմատիկական ֆունկցիաները `math` գրադարանում են (ինչպես և պետք էր սպասել)։

__8.__ Ներդրված գործողությունների ֆունկցիոնալ համարժեքները սահմանված են `operator` մոդուլում։

__9.__ Ծնող դասի կոնստրուկտորը կանչվում է `super()` գործողության միջոցով։ Օրինակ.
````python
>>> class A:
...   def __init__(self, l):
...     self.line = l

>>> class B(A):
...   def __init__(self, l):
...     super().__init__(self, l)

>>> b = B(777)
>>> print(b.line)
777
````

__10.__ Դասի համար կարելի է սահմանել միայն մեկ `__init__()` մեթոդ։

__11.__ `isinstance()` մեթոդը ստուգում է տրված օբյեկտի՝ տրված դասի նմուշ լինելը։
