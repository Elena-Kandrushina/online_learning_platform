from rest_framework import serializers


class YouTubeValidator:
    def __init__(self, field):
        self.field = field

    def __call__(self, data):
        url = data.get(self.field)

        if not url:
            return

        if 'youtube.com' not in url and 'youtu.be' not in url:
            raise serializers.ValidationError(
                {self.field: "Ссылка должна вести на YouTube"}
            )
