from .board_views import (
    board_list,
    board_create,
    board_detail,
    board_edit,
    board_delete
)

from .column_views import (
    column_create,
    column_edit,
    column_delete,
    update_column_position
)

from .task_views import (
    task_create,
    task_edit,
    task_delete,
    task_assign,
    task_detail,
    add_comment,
    add_attachment,
    update_task_position
)

from .comment_views import (
    delete_comment
)

from .label_views import (
    label_create,
    label_edit,
    label_delete
)

from .attachment_views import (
    delete_attachment
)

__all__ = [
    'board_list',
    'board_create',
    'board_detail',
    'board_edit',
    'board_delete',
    'column_create',
    'column_edit',
    'column_delete',
    'update_column_position',
    'task_create',
    'task_edit',
    'task_delete',
    'task_assign',
    'task_detail',
    'add_comment',
    'add_attachment',
    'update_task_position',
    'delete_comment',
    'delete_attachment',
    'label_create',
    'label_edit',
    'label_delete'
]
