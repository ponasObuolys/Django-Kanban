from django.db.models import Max
from ..models import Column

class ColumnService:
    @staticmethod
    def create_column(board, data):
        """Create a new column in the board"""
        # Get the next position
        max_position = board.columns.aggregate(Max('position'))['position__max']
        position = (max_position or 0) + 1
        
        # Create the column
        column = Column.objects.create(
            board=board,
            position=position,
            **data
        )
        
        return column

    @staticmethod
    def update_column(column, data):
        """Update column with provided data"""
        for key, value in data.items():
            setattr(column, key, value)
        column.save()
        return column

    @staticmethod
    def update_positions(columns_data):
        """Update positions of multiple columns"""
        for column_id, new_position in columns_data.items():
            Column.objects.filter(id=column_id).update(position=new_position)

    @staticmethod
    def delete_column(column):
        """Delete column and reorder remaining columns"""
        board = column.board
        old_position = column.position
        
        # Delete the column
        column.delete()
        
        # Reorder remaining columns
        Column.objects.filter(
            board=board,
            position__gt=old_position
        ).update(position=Max('position') - 1)
