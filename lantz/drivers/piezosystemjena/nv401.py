# -*- coding: utf-8 -*-

from lantz import Action, Feat
from lantz.messagebased import MessageBasedDriver
from lantz.errors import InstrumentError
from pyvisa import constants
import time


class nv401(MessageBasedDriver):
    """Driver for the nv401.
    """

    DEFAULTS = {'ASRL': {'write_termination': '\r',
                         'read_termination': '\r',
                         'baud_rate': 9600,
                         'parity': constants.Parity.none,
                         'stop_bits': constants.StopBits.one,
                         'encoding': 'ascii',
                         'timeout': 1000
                         }}

    #: flow control flags
    # RTSCTS = False
    # DSRDTR = False
    # XONXOFF = False

    def initialize(self):
        super().initialize()
        self.write('i1')
        self.write('cl')
        time.sleep(0.5)

    def query(self, command, *, send_args=(None, None), recv_args=(None, None)):
        """Send query to the stage and return the answer, after handling
        possible errors.

        :param command: command to be sent to the instrument
        :type command: string

        """
        ans = super().query(command, send_args=send_args, recv_args=recv_args)
        if 'err' in ans:
            code = ans.split(',')[1]
            if code == '1':
                raise InstrumentError('unknown command')
            elif code == '2':
                raise InstrumentError('too many characters in the command')
            elif code == '3':
                raise InstrumentError('too many characters in the parameter')
            elif code == '4':
                raise InstrumentError('too many parameter')
            elif code == '5':
                raise InstrumentError('wrong character in parameter')
            elif code == '6':
                raise InstrumentError('wrong separator')
            elif code == '7':
                raise InstrumentError('overload')
        return ans

    @Feat(units='micrometer')
    def position(self):
        ans = self.query('rd')
        return float(ans.split(',')[1])

    @position.setter
    def position(self, value):
        self.write('wr,{}'.format(round(value, 3)))

    @Action()
    def zero_position(self):
        self.write('wr,{}'.format(0))

    @Action(units='micrometer', limits=(100,))
    def moveAbsolute(self, value):
        self.write('wr,{}'.format(round(value, 3)))

    @Action(units='micrometer')
    def moveRelative(self, value):
        cur_pos = float(self.query('rd').split(',')[1])
        self.write('wr,{}'.format(round(cur_pos + value, 3)))