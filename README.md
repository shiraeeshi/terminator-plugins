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
