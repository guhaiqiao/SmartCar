# SmartCar

##  上位机功能
- 识别不同小车
- 生成路况
- 与小车同步路况
- 接收小车位置
- 强制减速命令

<!-- ##  connect

1.__car__ to __pc__:    `id + c(connect)`
2.__pc__ to __car__:    `id + a(accept)`
3.__car__ to __pc__:    `id + ok` `timout = 1s`

if timeout, repeated 2 -->


##  traffic information
1.__car__ to __pc__:

    id + r(request)

2.__pc__ to __car__:

    id + 1 + data(29 bytes) + check(1 byte)
    id + 2 + data(29 bytes) + check(1 byte)
    id + 3 + data(29 bytes) + check(1 byte)
3.__car__ to __pc__:

    id + o(ok)

##  position synchronize
1.__car__ to __pc__:

    id + p(position) + x + 000 + y + 000 + z + 000 + check(1 byte)
    15 bytes in total

2.__pc__ to __car__:
- right

        id + s(slowdown) + 00% + check(1 byte)
        6 bytes in total
- wrong (__car__ will resend the position)

        id + p(position)

3.__car__ to __pc__:
- right (according to the check byte)

        id + o(ok)
- wrong (__pc__ will resend the slowdown)

        id + s(slowdown)
##  timeout and data lost
### timeout
- All the timeout is 0.5s.
- Over the time will make the side to send resend all the data last sent and the timeout will double itself.
### data lost

- __car__  receive some wrong traffic information
  - __car__ to __pc__:

        id + t(traffic) + 0(number of the wrong information) + 1/2/3(order)
  - __pc__ to __car__:

        id + 0(order) + data(29 bytes) + check(1 byte)
  - __car__ to __pc__:

        id + o(ok)
- __car__ did not receive all the traffic information (time is out) (the serial.read timeout should be shorter than 0.5s)
  - clear the data received just now
  - receive all the data again