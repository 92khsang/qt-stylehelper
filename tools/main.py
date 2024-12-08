from pathlib import Path

from qt_stylehelper.value_object import Theme

from qt_stylehelper import StaticBuiltInResourceGenerator

StaticBuiltInResourceGenerator.generate(
	"dark_amber",
	destination_dir=str(Path(__file__).parent.resolve() / "resources"),
	qrc_name="_stylehelper.qrc",
)

custom_theme = Theme(
	{
		"primaryColor"       : "#00bcd4",
		"primaryLightColor"  : "#62efff",
		"secondaryColor"     : "#f5f5f5",
		"secondaryLightColor": "#e6e6e6",
		"secondaryDarkColor" : "#ffffff",
		"primaryTextColor"   : "#3c3c3c",
		"secondaryTextColor" : "#555555",
	}
)

StaticBuiltInResourceGenerator.generate_custom_theme(
	"custom_theme",
	custom_theme,
	destination_dir=str(Path(__file__).parent.resolve() / "resources"),
	qrc_name="_stylehelper.qrc",
)