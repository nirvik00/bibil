import System.Drawing
import System.Windows.Forms
from System.Drawing import *
from System.Windows.Forms import *

class UIForm(Form):
    def __init__(self, title):
        self.Text = title
        self.panel = UIPanel()
        self.Width = 550
        self.Height = 1050
        #self.StartPosition=FormStartPosition.Manual.CenterScreen
        self.StartPosition=FormStartPosition.Manual
        self.Top=0
        self.Left=0
        
        
    def layoutControls(self):
        #self.AutoSize = True
        self.ShowInTaskbar = True
        self.MaximizeBox = False
        self.MinimizeBox = True
        self.ShowIcon = False
        self.FormBorderStyle = FormBorderStyle.FixedToolWindow
        
        
        self.SuspendLayout()
        self.panel.layoutControls()
        self.Controls.Add(self.panel)
        
        ctrlList = self.panel.Controls.Find("Cancel", True)
        if (len(ctrlList) != 0):
            c = ctrlList[0]
            self.CancelButton = c
        self.ResumeLayout(False)

class UIPanel(FlowLayoutPanel):
    def __init__(self):
        self.controls = [] # The list of controls the panel accumulates as code adds them
        self.tabIndex = 0 # Each control added uses this tabIndex and then increments it

        self.AutoSize = True
        self.AutoScroll = True 
        self.FlowDirection = FlowDirection.LeftToRight
        self.WrapContents = True
    
    def addSeparator(self, name, width, breakFlowAfter):
        c = GroupBox()
        c.Size = System.Drawing.Size(width, 8) # 8 makes it a horizontal bar
        c.Margin = System.Windows.Forms.Padding(3, 6, 3, 10) # 5 is to align with other controls vertically
        c.TabStop = False
        self.SetFlowBreak(c, breakFlowAfter)
        self.controls.append(c)
        return c
    
    def addLabel(self, name, text, color, breakFlowAfter):
        c = Label()
        c.Name = name
        c.Text = text
        if (color != None):
            clr = System.Drawing.Color.FromArgb(color[0], color[1], color[2])
            c.ForeColor = clr
        c.AutoSize = True
        c.Margin = System.Windows.Forms.Padding(3, 5, 3, 0) # 5 is to align with other controls vertically
        self.SetFlowBreak(c, breakFlowAfter)
        self.controls.append(c)
        return c
    
    def addLinkLabel(self, name, text, URL, breakFlowAfter, delegate):
        c = LinkLabel()
        c.Tag = URL # Stuff the URL here so the event handler can get it :)
        c.Text = text
        c.AutoSize = True
        c.TabStop = False
        c.Margin = System.Windows.Forms.Padding(3, 5, 3, 0) # 5 is to align with other controls vertically
        self.SetFlowBreak(c, breakFlowAfter)
        if (delegate != None):
            c.LinkClicked += delegate
        else:
            c.LinkClicked += self.linkLabel_LinkClicked
        self.controls.append(c)
        return c
        
    def linkLabel_LinkClicked(self, sender, e):
        try:
            # Open the default browser with a URL:
            System.Diagnostics.Process.Start(sender.Tag)
            sender.LinkVisited = true;
        except:
            pass
    
    def addPictureBox(self, name, filename, breakFlowAfter):
        c = PictureBox()
        c.Name = name
        try:
            image = Image.FromFile(filename)
            c.Image = image
            c.Height = image.Height
            c.Width = image.Width
            self.SetFlowBreak(c, breakFlowAfter)
            self.controls.append(c)
            return c
        except:
            print "Error: Could not load image "+filename
            return None
        
    def addTextBox(self, name, text, width, breakFlowAfter, delegate):
        c = TextBox()
        c.Name = name
        c.Text = text
        c.Size = System.Drawing.Size(width, 23)
        c.TabIndex = self.tabIndex; self.tabIndex += 1
        if (delegate != None):
            c.TextChanged += delegate
        self.SetFlowBreak(c, breakFlowAfter)
        self.controls.append(c)
        return c
    
    def addReadonlyText(self, name, text, width, breakFlowAfter):
        c = Label()
        c.Name = name
        c.Text = text
        c.TabStop = False
        c.AutoEllipsis = True
        c.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D
        c.Size = System.Drawing.Size(width, 23)
        c.Enabled = False
        c.Margin = System.Windows.Forms.Padding(3, 3, 3, 3)
        c.Padding = System.Windows.Forms.Padding(3, 3, 3, 3) 
        self.SetFlowBreak(c, breakFlowAfter)
        self.controls.append(c)
        return c
    
    def addCheckBox(self, name, text, checked, breakFlowAfter, delegate):
        c = CheckBox()
        c.Name = name
        c.Text = text
        c.AutoSize = True
        c.Checked = checked
        c.TabIndex = self.tabIndex; self.tabIndex += 1
        if (delegate != None):
            c.CheckStateChanged += delegate
        self.SetFlowBreak(c, breakFlowAfter)
        self.controls.append(c)
        return c
    
    def addButton(self, name, text, width, breakFlowAfter, delegate):
        c = Button()
        c.AutoSizeMode = AutoSizeMode.GrowAndShrink
        c.AutoEllipsis = False
        c.Name = name
        c.Text = text
        c.TabIndex = self.tabIndex; self.tabIndex += 1
        if (delegate != None):
            c.Click += delegate
        if (width != None):
            c.Width = width
        else:
            c.AutoSize = True
        # Special case the OK and Cancel buttons so they work as expected
        if (text == "OK"):
            c.DialogResult = DialogResult.OK
        elif (text == "Cancel"):
            c.DialogResult = DialogResult.Cancel
        self.SetFlowBreak(c, breakFlowAfter)
        self.controls.append(c)
        return c
    
    def addComboBox(self, name, items, initialIndex, breakFlowAfter, delegate):
        c = ComboBox()
        c.Name = name
        for item in items:
            c.Items.Add(item)
        c.DropDownStyle = ComboBoxStyle.DropDownList # So you can't type into it
        c.SelectedIndex = initialIndex
        c.TabIndex = self.tabIndex; self.tabIndex += 1
        if (delegate != None):
            c.SelectedIndexChanged += delegate
        self.SetFlowBreak(c, breakFlowAfter)
        self.controls.append(c)
        return c
    
    def addNumericUpDown(self, name, lowerLimit, upperLimit, increment, \
        decimalPlaces, initValue, width, breakFlowAfter, delegate):
        c = NumericUpDown()
        c.BeginInit()
        c.Name = name
        c.TabIndex = self.tabIndex; self.tabIndex += 1
        if (delegate != None):
            c.ValueChanged += delegate
        c.Minimum = lowerLimit
        c.Maximum = upperLimit
        c.Increment = increment
        c.DecimalPlaces = decimalPlaces
        c.Value = initValue
        if (width != None):
            c.Width = width
        self.SetFlowBreak(c, breakFlowAfter)
        self.controls.append(c)
        c.EndInit()
        return c

    def addTrackBar(self, name, lowerLimit, upperLimit, smallChange, largeChange, tickFrequency, initValue, width, breakFlowAfter, delegate):
        c = TrackBar()
        c.BeginInit()
        c.Name = name
        c.TabIndex = self.tabIndex; self.tabIndex += 1
        if (width != None):
            c.Width = width
        if (delegate != None):
            c.ValueChanged += delegate
        c.Minimum = lowerLimit
        c.Maximum = upperLimit
        c.SmallChange = smallChange
        c.LargeChange = largeChange
        if (tickFrequency != None):
            c.TickFrequency = tickFrequency
        c.Value = initValue
        self.SetFlowBreak(c, breakFlowAfter)
        self.controls.append(c)
        c.EndInit()
        return c

    def layoutControls(self):
        self.SuspendLayout()
        self.AutoSize = True
        self.AutoSizeMode = AutoSizeMode.GrowAndShrink
        for c in self.controls:
            self.Controls.Add(c)
        self.ResumeLayout(False)

if( __name__ == "__main__" ):
    print "No Syntax Errors"