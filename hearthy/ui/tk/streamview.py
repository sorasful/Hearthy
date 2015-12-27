import tkinter
from tkinter import ttk

def _append_node(tree, node, key, value):
    def add_sub(elements, summary=None):
        if summary is None:
            summary = '({0} element{1})'.format(len(elements), '' if len(elements) == 1 else 's')
        subnode = tree.insert(node, 'end', text=key, value=(summary, ''))
        for subkey, subval in elements:
            _append_node(tree, subnode, subkey, subval)
    if isinstance(value, str):
        tree.insert(node, 'end', text=key, value=(value, ''))
    elif isinstance(value, int):
        tree.insert(node, 'end', text=key, value=(value, ''))
    elif hasattr(value, 'ListFields'):
        add_sub([(d.name, v) for d, v in value.ListFields()], value.__class__.__name__)
    else:
        add_sub([('[{0}]'.format(i), value[i]) for i in range(len(value))])

class StreamView:
    def __init__(self, stream_id, start):
        self._n_packets = 0
        self.cb = None
        self._start = start
        self._stream_id = stream_id
        self._build_widgets()

    def _on_destroy(self):
        if self.cb is not None:
            self.cb(self, 'destroy')
        self._window.destroy()

    def _build_widgets(self):
        self._window = parent = tkinter.Toplevel()
        parent.title('Stream {0}'.format(self._stream_id))
        parent.protocol('WM_DELETE_WINDOW', self._on_destroy)

        tree = ttk.Treeview(parent, columns=('Value', 'Time'))
        tree.heading('#0', text='Name', anchor='w')
        tree.heading('#1', text='Value', anchor='w')
        tree.heading('#2', text='Time', anchor='w')

        tree.column('#0', stretch=True)
        tree.column('#1', stretch=False)
        tree.column('#2', stretch=False)

        tree.tag_configure(0, background='#F0A57D')
        tree.tag_configure(1, background='#7DC8F0')

        vsb = ttk.Scrollbar(parent, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)

        tree.grid(column=0, row=0, sticky='nsew')
        vsb.grid(column=1, row=0, sticky='ns')

        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        self._tree = tree

    def process_packet(self, packet, who, ts):
        name = packet.__class__.__name__
        time = '{0:0.2f}s'.format((ts-self._start)/1000)
        
        tree = self._tree
        node = tree.insert(
                '', 'end',
                text='Packet {0}'.format(self._n_packets),
                value=(name, time),
                tags=(who,))
        self._n_packets += 1

        for desc, subval in packet.ListFields():
            _append_node(tree, node, desc.name, subval)
