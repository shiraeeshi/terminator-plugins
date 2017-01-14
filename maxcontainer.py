
import gtk

import terminatorlib.plugin as plugin

AVAILABLE = ['MaximizeContainerPlugin']

from terminatorlib.factory import Factory
maker = Factory()

class MaximizeContainerPlugin(plugin.Plugin):
    capabilities = ['terminal_menu']

    is_selecting = False
    is_maximized = False
    root_to_add = False
    window = False
    was_first = False
    former_parent = False
    closeterm_handler_id = False

    def do_select_container(self, terminal):
        self.is_selecting = True
        window = terminal.get_toplevel()
        root = window.get_child()
        current_selected_level = [0]
        parents = build_parents_list(terminal, root)
        def draw_first_terminal(widget, event):
            draw_as_selected(parents[-1])
            return(False)
        redraw_handler_id = terminal.vte.connect_after('expose-event', draw_first_terminal)
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
                level = current_selected_level[0]
                if level == len(parents) - 1:
                    redraw(root)
                    self.is_selecting = False
                    terminal.vte.disconnect(redraw_handler_id)
                    terminal.vte.get_window().process_updates(True)
                    window.disconnect(keypress_handler_id)
                    return(True)
                redraw(root)
                parent = parents[-1-level]
                former_parent = parents[-2-level]
                window.remove(root)
                former_parent.remove(parent)
                window.add(parent)
                all_terminals = collect_terminals(parent)
                term_count = [len(all_terminals)]
                def close_handler(widget):
                    term_count[0] -= 1
                    if term_count[0] == 0:
                        self.unmaximize(widget)
                        return(True)
                    else:
                        return(False)
                for term in all_terminals:
                    term.connect('close-term', close_handler)
                terminal.grab_focus()
                self.window = window
                self.former_parent = former_parent
                self.was_first = former_parent.get_child1() == parent
                self.root_to_add = root
                self.is_selecting = False
                terminal.vte.disconnect(redraw_handler_id)
                terminal.vte.get_window().process_updates(True)
                window.disconnect(keypress_handler_id)
                self.is_maximized = True
                return(True)
            if keyval_name == 'Escape':
                redraw(root)
                self.is_selecting = False
                terminal.vte.disconnect(redraw_handler_id)
                terminal.vte.get_window().process_updates(True)
                window.disconnect(keypress_handler_id)
                return(True)
            return(False)
        keypress_handler_id = window.connect('key-press-event', keypress_handler)

    def unmaximize(self, terminal = None):
        unmaximized = self.window.get_children()[0]
        self.window.remove(unmaximized)
        self.window.add(self.root_to_add)
        if self.was_first:
            second = self.former_parent.get_children()[0]
            self.former_parent.add(unmaximized)
            self.former_parent.add(second)
        else:
            self.former_parent.add(unmaximized)
        if terminal:
            terminal.grab_focus()

        self.former_parent = False
        self.was_first = False
        self.root_to_add = False
        self.window = False
        self.is_maximized = False

    def callback(self, menuitems, menu, terminal):
        """Add out menu item to the menu"""
        if self.is_maximized:
            item = gtk.MenuItem('Unmaximize container')
            item.set_sensitive(not terminal.is_zoomed())
            item.connect('activate', lambda x: self.unmaximize(terminal))
            menuitems.append(item)
            return
        item = gtk.MenuItem('Maximize container...')

        is_single = terminal.get_toplevel().get_child() == terminal

        item.set_sensitive(not terminal.is_zoomed() and not self.is_selecting and not is_single)
        item.connect('activate', lambda x: self.do_select_container(terminal))
        menuitems.append(item)

def collect_terminals(component):
    if not maker.isinstance(component, 'Container'):
        raise Error('component is not a Container')
    terminals = []
    children = component.get_children()
    for child in children:
        if maker.isinstance(child, 'Terminal'):
            terminals.append(child)
        elif maker.isinstance(child, 'Container'):
            terminals += collect_terminals(child)
        else:
            raise Error('unknown element: %s' % start)
    return terminals

def build_parents_list(terminal, root):
    def dfs(start, acc):
        if maker.isinstance(start, 'Terminal'):
            if start == terminal:
                return (True, acc)
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
    widget.set_colors(terminal.fgcolor_inactive, terminal.bgcolor,
                        terminal.palette_inactive)
    terminal.set_cursor_color()
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
    widget.set_colors(terminal.bgcolor, terminal.fgcolor_inactive,
                        terminal.palette_inactive)
    alloc = widget.get_allocation()
    #redraw by forcing an event
    widget.queue_draw_area(0, 0, alloc.width, alloc.height)
    widget.get_window().process_updates(True)

