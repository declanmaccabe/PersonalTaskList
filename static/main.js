// Small JS helper to handle edit modal population
console.log('Task list loaded');

document.addEventListener('DOMContentLoaded', function () {
	// delegate to all edit buttons
	const editButtons = document.querySelectorAll('.edit-btn');
	editButtons.forEach(btn => {
		btn.addEventListener('click', function (e) {
			const id = this.dataset.id;
			const title = this.dataset.title || '';
			const description = this.dataset.description || '';
			const status = this.dataset.status || 'New';
			const planned = this.dataset.planned || '';
			const due = this.dataset.due || '';

			// populate modal fields
			document.getElementById('edit-title').value = title;
			document.getElementById('edit-description').value = description;
			document.getElementById('edit-status').value = status;
			document.getElementById('edit-planned').value = planned === 'None' ? '' : (planned || '');
			document.getElementById('edit-due').value = due === 'None' ? '' : (due || '');

			// set form action
			const form = document.getElementById('editTaskForm');
			form.action = `/edit/${id}`;

			// show modal via bootstrap
			const editModalEl = document.getElementById('editTaskModal');
			const modal = new bootstrap.Modal(editModalEl);
			modal.show();
		});
	});
});
