from decimal import Decimal, Context, getcontext, setcontext, localcontext

one = Decimal('1')
three = Decimal('3')



with localcontext(Context(prec=5)), open("out.txt", 'w') as mytxt:
    mytxt.write(f"{one} / {three} = {one / three}\n")
print(one / three)





# original_context = getcontext()
# new_context = Context(prec=4)
# setcontext(new_context)

# try:
#     print(new_context)
#     print(one / three)
# finally:
#     setcontext(original_context)
# print(one / three)

