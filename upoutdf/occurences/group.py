# coding: utf-8

from hashlib import md5

from upoutdf.duration import Duration

class OccurenceGroup(object):

    _blocks = []

    def __init__(self,blocks):
        self._blocks = blocks

    def __hash__(self):
        list = []

        for b in self._blocks:
            list.append(b.__hash__())

        #occurence hash returns md5, which is case insensitive
        return md5(" ".join(sorted(list, key=str.lower))).hexdigest()

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return self.__hash__() == other.__hash__() 

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_blocks(self):
        return self._blocks
        
    def _get_earliest_block(self):
        earliest = None
        for block in self._blocks:
            if earliest is None:
                earliest = block

            if block.unix_starting_date < earliest.unix_starting_date:
                earliest = block

        return earliest

    def _get_latest_block(self):
        latest = None
        for block in self._blocks:
            if latest is None:
                latest = block

            if block.unix_ending_date > latest.unix_ending_date:
                latest = block

        return latest

    @property
    def total_timeframes(self):
        total = 0
        for block in self._blocks:
            total += len(block.get_occurences())

        return total

    @property
    def starting_date(self):
        block = self._get_earliest_block()
        return block.starting_date

    @property
    def ending_date(self):
        block = self._get_latest_block()
        return block.ending_date

    @property
    def starting_date_infinite(self):
        block = self._get_earliest_block()
        return block.starting_date_infinite

    @property
    def ending_date_infinite(self):
        block = self._get_latest_block()
        return block.ending_date_infinite

    @property
    def unix_starting_date(self):
        block = self._get_earliest_block()
        return block.unix_starting_date

    @property
    def unix_ending_date(self):
        block = self._get_latest_block()
        return block.unix_ending_date

    def add_block(self,block):
        self._blocks.append(block)

    def get_duration(self):
        return Duration(
            start=self.unix_starting_date,
            end=self.unix_ending_date
        )

