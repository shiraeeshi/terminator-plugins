
import gtk

import terminatorlib.plugin as plugin

AVAILABLE = ['MaximizeContainerPlugin']

from terminatorlib.factory import Factory
maker = Factory()

class MaximizeContainerPlugin(plugin.Plugin):
    capabilities = ['terminal_menu']

    parent_to_remove = False
    root_to_add = False
    window = False
    was_first = False
    parents_parent = False

    def do_select_container(self, terminal):
        window = terminal.get_toplevel()
        root = window.get_child()
        current_selected_level = [0]
        parents = build_parents_list(terminal, root)
        def keypress_handler(widget, event):
            # Workaround for IBus intefering with broadcast when using dead keys
            # Environment also needs IBUS_DISABLE_SNOOPER=1, or double chars appear
            # in the receivers.
            if (event.state | gtk.gdk.MODIFIER_MASK ) ^ gtk.gdk.MODIFIER_MASK != 0:
                #dbg('Terminal::on_keypress: Ingore processed event with event.state %d' % event.state)
                return(False)
            keyval_name = gtk.gdk.keyval_name(event.keyval)
            if keyval_name == 'Up':
                if current_selected_level[0] < len(parents)-1:
                    current_selected_level[0] += 1
                parent = parents[-1-current_selected_level[0]]
                redraw(root)
                draw_as_selected(parent)
                return(True)
            if keyval_name == 'Down':
                if current_selected_level[0] > 0:
                    current_selected_level[0] -= 1
                parent = parents[-1-current_selected_level[0]]
                redraw(root)
                draw_as_selected(parent)
                return(True)
            if keyval_name == 'Return':
                redraw(root)
                level = current_selected_level[0]
                if level == 0 or level == len(parents) - 1:
                    terminal.vte.disconnect(handler_id)
                    return(True)
                parent = parents[-1-level]
                parents_parent = parents[-2-level]
                window.remove(root)
                parents_parent.remove(parent)
                window.add(parent)
                terminal.grab_focus()
                self.window = window
                self.parent_to_remove = parent
                self.parents_parent = parents_parent
                self.was_first = parents_parent.get_child1() == parent
                self.root_to_add = root
                terminal.vte.disconnect(handler_id)
                return(True)
            return(False)
        handler_id = terminal.vte.connect('key-press-event', keypress_handler)

    def unmaximise(self, terminal):
        self.window.remove(self.parent_to_remove)
        if self.was_first:
            second = self.parents_parent.get_children()[0]
            self.parents_parent.add(self.parent_to_remove)
            self.parents_parent.add(second)
        else:
            self.parents_parent.add(self.parent_to_remove)
        self.window.add(self.root_to_add)
        terminal.grab_focus()

        self.parent_to_remove = False
        self.parents_parent = False
        self.was_first = False
        self.root_to_add = False
        self.window = False

    def callback(self, menuitems, menu, terminal):
        """Add out menu item to the menu"""
        if self.parent_to_remove:
            item = gtk.MenuItem('Unmaximize container')
            item.set_sensitive(not terminal.is_zoomed())
            item.connect('activate', lambda x: self.unmaximise(terminal))
            menuitems.append(item)
            return
        item = gtk.MenuItem('Maximize container...')
        item.set_sensitive(not terminal.is_zoomed())
        item.connect('activate', lambda x: self.do_select_container(terminal))
        menuitems.append(item)

def build_parents_list(terminal, root):
    def dfs(start, acc):
        if maker.isinstance(start, 'Terminal'):
            if start == terminal:
                return (True, acc + [terminal])
            else:
                return (False, None)
        elif maker.isinstance(start, 'Container'):
            children = start.get_children()
            for child in children:
                (found, parents_lst) = dfs(child, acc + [start])
                if found:
                    return (True, parents_lst)
            return (False, None)
        else:
            raise Error('unknown element: %s' % start)
    (found, parents_lst) = dfs(root, [])
    if not found:
        raise Error('cannot find terminal')
    return parents_lst


def redraw(component):
    if maker.isinstance(component, 'Container'):
        children = component.get_children()
        for child in children:
            redraw(child)
        return
    if not maker.isinstance(component, 'Terminal'):
        raise Error('wrong component type (not Terminal or Container)')
    terminal = component
    widget = terminal.vte
    alloc = widget.get_allocation()
    widget.queue_draw_area(0, 0, alloc.width, alloc.height)

def draw_as_selected(component):
    if maker.isinstance(component, 'Container'):
        children = component.get_children()
        for child in children:
            draw_as_selected(child)
        return
    if not maker.isinstance(component, 'Terminal'):
        raise Error('wrong component type (not Terminal or Container)')
    terminal = component
    widget = terminal.vte
    if terminal.config['use_theme_colors']:
        color = terminal.vte.get_style().text[gtk.STATE_NORMAL]
    else:
        color = gtk.gdk.color_parse(terminal.config['foreground_color'])
    alloc = widget.get_allocation()
    topleft = (0, 0)
    topright = (alloc.width, 0)
    bottomleft = (0, alloc.height)
    bottomright = (alloc.width, alloc.height)
    coord = (topleft, topright, bottomright, bottomleft)
    #here, we define some widget internal values
    widget._draw_data = { 'color': color, 'coord' : coord }
    #redraw by forcing an event
    def on_expose_event(widget, _event):
        """Handle an expose event while dragging"""
        if not widget._draw_data:
            return(False)

        context = widget.window.cairo_create()
        color = widget._draw_data['color']
        coord = widget._draw_data['coord']

        context.set_source_rgba(color.red, color.green, color.blue, 0.5)
        if len(coord) > 0 :
            context.move_to(coord[len(coord)-1][0], coord[len(coord)-1][1])
            for i in coord:
                context.line_to(i[0], i[1])

        context.fill()
        return(False)
    connec = widget.connect_after('expose-event', on_expose_event)
    widget.queue_draw_area(0, 0, alloc.width, alloc.height)
    widget.get_window().process_updates(True)
    #finaly reset the values
    widget.disconnect(connec)
    widget._draw_data = None
