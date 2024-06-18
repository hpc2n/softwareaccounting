# Contribution guidelines

## Core guidelines

* Code should be compatible with Python 3.6 in general.

* Avoid dependencies that are not completely necessary.

* The code is deceptively copmlicated due to multi-threading; hence, pay extra attention to the clarity of your code.

* The implementation of all guidelines in this document, as well as their exact form, is subject to ongoing revision as of 2024-06-18.

## General guidelines

* Use [expressive function and variable names](https://xkcd.com/910/), e.g.,
  * Good: `get_value` (function or method returning something), `value` (property), `compute_value` (subroutine-like behavior that does *not* return a result but changes existing data structures)
  * Avoid: `get_val`, `v`, `val`, `calc_val` or similar

* Consider carefully which methods and attributes of an object are to be exposed to other objects. As is usual in Python, prepend attributes not to be exposed with an underscore `_`. If you want an attrbiute to be exposed but not directly modifiable, make it a property:

```python
class Dog:
    def __init__(self, age: int = 5):
        self._age = age

    @property
    def age(self) -> int:
        return self._age
```

* Avoid using reserved keywords like `id` in variable names.

* Prefer inline format strings for readability whenever possible.

### Prefer NOT to do this:

```python
theword = 'out'
fstring_a = 'Who let %d dogs %s?' % (100, theword)
fstring_b = 'Who let {:d} dogs {:s}?' % (100, theword)
```

### Prefer the inline style:

```python
theword = 'out'
fstring_a = f'Who let {100:d} dogs {theword:s}?'
# Sometimes, this style is necessary:
base_string = f'Who let {:d} dogs {:s}?'
...
parsed_string = base_string.format(100, theword)
```

* Don't use `map` or `filter`, use list comprehension for readability and clarity:

### Do NOT do this:

```python
a = list(map(hash, ['a', 'b', 'c']))
b = list(filter(lambda x: x < 10, [1, 27, 3.1]))
```

### Do this instead:

```python
a = [hash(s) for s in ['a', 'b', 'c']]
b = [i for i in [1, 27, 3.1] if i < 10]
```

* Use the `@property` decorator when applicable to create functions that behaves like constants or variables,
but allows more control over getting and setting.

```python
Class Dog:
    def __init__(self,
                 name_of_dog: str = 'Fido',
                 weight: int = 10,
                 age: int = 3):
        self._name_of_dog = name_of_dog
        self._age = age
        self._weight = weight

    @property
    def name_of_dog(self) -> str:
        """ Dog name. """
        return self._name_of_dog

    @name_of_dog.setter
    def name_of_dog(self, value: str) -> None:
        if self._age >= 3:
            raise ValueError('Dog is too old to change the name!')
        self._name_of_dog = value

    @property
    def nickname(self) -> str:
        """ Nickname of the dog. Follows from the name and weight. """
        if self._weight < 20:
            return f'Little {self.name_of_dog}'
        return f'Big {self.name_of_dog}'


>>> dog = Dog()
>>> print(dog.nickname)
Little Fido
>>> dog.name_of_dog = 'Brutus'
ValueError: Dog is too old to change the name!
>>> dog2 = Dog(age=2)
>>> dog2.name_of_dog = 'Brutus'
>>> print(dog2.nickname)
Little Brutus
```

* Try to add docstrings and, if necessary comments, to any new code, and we will gradually update old code with these features.
  We will use the [NumPy docstring style](http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_numpy.html) throughout.
  With respect to inline comments, remember that _clearly written code_ is always better than inline comments. Do not comment excessively.

* We will use `flake8` to enforce `PEP8` and `pyflakes` guidelines (gradually).
  To check the compliance of your code locally, use [`flake8`](https://flake8.pycqa.org/). This can be added to most IDE:s.
  The code base uses single quotes ( `'`) for regular strings and triple double quotes (`"""`) for multi-line strings.
  We will use a maximum of `110` character lines.

* Please use spaces, not tabs.

* For `dict`s where all keys are valid-keyword strings, use the keyword-style constructor for better readability:

### DON'T:
```python
mydict = {'blue': 'my_favourite_color', 'no': 'yellow'}
```

### Do this instead:
```python
mydict = dict(blue='my_favourite_color', no='yellow')
```

### You can use curly braces if necessary and neat:

```python
a = hash('blue')
b = hash('no')
# Prefer to wrap in dict()
mydict = dict({a: 'my_favourite_color', b: 'yellow'})
# Or do this instead
mydict = dict()
mydict[a] = 'my_favourite_color'
mydict[b] = 'yellow'
```

* Avoid the C-style "exploded" brackets of _e.g._, `Black` and instead use `Lisp`-style brackets. In other words,

### Do not write:
```python
annoyingly_long_variable_name = set(
    [
        a for a in
        list(
            'abcdefg'
        )
        if a not in compare_string(
            my,
            set,
            of,
            params,
        )
    ],
)
```

### Instead write:
```python
annoyingly_long_variable_name = set(
    [a for a in list('abcdefg') if a not in compare_string(my, set, of, params)])
```

Note that to this end, there is no need to use automated code formatters. Manual code formatting with a good IDE should be efficient enough.

* Use type hints, including ones from e.g. `from typing import Dict`, to maintain readability and compatibility with Python 3.6.
Prefer `Iterable` to `List`. For class object instances, just use the class name. For example:

```python

Class Dog:
    def __init__(self,
             name: str,
             has_bone: bool):
        self.name = name
        self.has_bone = has_bone

    def bark() -> None:
        if self.has_bone:
            print('Woof!')
            return
        print('Grrr!')


def get_dog_farm(alpha_male: Dog,
                 names_of_dogs: Iterable[str],
                 number_of_dogs: int = 5,
                 number_of_bones: int = 3) -> Dict:
    dog_farm = dict()
    for name in names_of_dogs:
        has_bone = number_of_bones > 0
        if has_bone:
            number_of_bones -= 1
        dog_farm[name] = Dog(name=name, has_bone=has_bone)
        ...
        number_of_dogs -= 1
    ...
    alpha_male.bark()
    assert number_of_dogs == 0
    assert number_of_bones == 0
    return dog_farm
```

The function `get_dog_farm` is strange and potentially complicated, but using the type hints we can at least see what kinds of arguments it should take and return.
