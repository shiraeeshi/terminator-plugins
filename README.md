# terminator-plugins

## maxcontainers - maximize containers*

\* Works with the gtk2-version of terminator, tested with 0.98 version.

Terminator allows to maximize a single terminal, but what if I want to maximize more than one? This plugin does just that.

1. Right-click on the terminal and select the "Maximize container..." menu item.
2. Select a container to maximize using "up" and "down" buttons.
3. Press "enter" to maximize or "escape" to cancel.
4. To unmaximize right-click and select the "Unmaximize container" menu item.

Let's say you're going through some tutorial and you want to open 4 terminals:

1. Tutorial text
2. Where you edit files
3. Where you run curl commands
4. Where you run the server

![Four terminals numbered](https://github.com/shiraeeshi/terminator-plugins/raw/master/images/maxcontainer_1_with_numbers.png "Four terminals numbered")

(Two empty terminals in the image are just for demonstration.)

When you are editing files, you want to see only first two of them, and when you're done you want terminator to show all of them to see the results.

Right-click on one of two terminals you're going to maximize and select "Maximize container..." menu item:

![Menu when maximizing](https://github.com/shiraeeshi/terminator-plugins/raw/master/images/maxcontainer_2.png "Menu when maximizing")

After that you enter the "container selection mode", in which you can select a container moving up and down in the containers hierarchy using "up" and "down" buttons.

![Container selection mode](https://github.com/shiraeeshi/terminator-plugins/raw/master/images/maxcontainer_container_selection.gif "Container selection mode")

Select a needed container and press "enter" to maximize. Now you see two terminals in the window:

![Maximized container](https://github.com/shiraeeshi/terminator-plugins/raw/master/images/maxcontainer_4.png "Maximized container")

When you want to "unmaximize" right-click and select the "Unmaximize container" menu item:

![Menu when unmaximizing](https://github.com/shiraeeshi/terminator-plugins/raw/master/images/maxcontainer_5.png "Menu when unmaximizing")

Terminator unmaximizes the container and you see all terminals again:

![Unmaximized](https://github.com/shiraeeshi/terminator-plugins/raw/master/images/maxcontainer_6.png "Unmaximized")

---
Note:
There is a subtle difference between closing a Terminator window and closing a terminal.
Normally, Terminator asks the user for a confirmation when he's trying to close a window that contains more than one terminal. But in maximized mode Terminator "forgets" about the hidden terminals when closing a window - it doesn't show any dialog and silently closes the window and all the terminals. (You close a window using "alt-f4" combination or pressing on cross sign on window's header.)
When closing a maximized terminal Terminator unmaximizes it and shows the hidden terminals. (You close a terminal using "ctrl-shift-w" combination or using the "close" menu item in popup menu.)

It means that closing a window is risky, it's possible for you to forget about the hidden terminals and accidentally close all of them, and Terminator won't ask you about them. On the other hand, closing a terminal is always safe.

The cause of this bug is in the Terminator's codebase, in window.py:

```python

def on_delete_event(self, window, event, data=None):
    """Handle a window close request"""
    maker = Factory()
    if maker.isinstance(self.get_child(), 'Terminal'):
        dbg('Window::on_delete_event: Only one child, closing is fine') # What about hidden terminals?
        return(False)
    elif maker.isinstance(self.get_child(), 'Container'):
        return(self.confirm_close(window, _('window')))
```

So, to resume, a little advise:
When you're closing a Terminator window, be careful and make sure that you haven't forgotten about hidden terminals.
Or don't close the window at all, just close the terminal.
