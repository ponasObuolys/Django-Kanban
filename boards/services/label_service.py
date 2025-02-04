from ..models import Label

class LabelService:
    @staticmethod
    def create_label(board, data):
        """Create a new label for a board."""
        label = Label.objects.create(
            board=board,
            name=data['name'],
            color=data['color']
        )
        return label
    
    @staticmethod
    def update_label(label, data):
        """Update an existing label."""
        label.name = data['name']
        label.color = data['color']
        label.save()
        return label
    
    @staticmethod
    def get_board_labels(board):
        """Get all labels for a board."""
        return Label.objects.filter(board=board).order_by('name') 