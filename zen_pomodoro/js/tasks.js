/**
 * Zen Task Manager Module
 * Manages daily task lists, active task selection, and LocalStorage sync.
 */

class TaskManager {
    constructor() {
        this.tasks = JSON.parse(localStorage.getItem('zen_tasks')) || [
            { id: 1, title: 'Deep work on project architecture', est: 3, done: 0, completed: false },
            { id: 2, title: 'Review pull requests and code docs', est: 1, done: 1, completed: true }
        ];
        this.activeTaskId = 1;

        this.tasksListEl = document.getElementById('tasksList');
        this.taskCounterEl = document.getElementById('taskCounter');
        this.addTaskForm = document.getElementById('addTaskForm');
        this.taskInput = document.getElementById('taskInput');
        this.taskEstInput = document.getElementById('taskEstInput');
        this.activeTaskPill = document.getElementById('activeTaskPill');
        this.activeTaskTitle = document.getElementById('activeTaskTitle');

        this.init();
    }

    init() {
        if (this.addTaskForm) {
            this.addTaskForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.addTask(this.taskInput.value.trim(), parseInt(this.taskEstInput.value, 10) || 1);
                this.taskInput.value = '';
            });
        }

        // Listen for timer completion to increment active task count
        document.addEventListener('pomoCompleted', () => {
            if (this.activeTaskId) {
                const task = this.tasks.find(t => t.id === this.activeTaskId);
                if (task) {
                    task.done++;
                    this.save();
                    this.render();
                }
            }
        });

        this.render();
    }

    addTask(title, est) {
        if (!title) return;
        const newTask = {
            id: Date.now(),
            title: title,
            est: est,
            done: 0,
            completed: false
        };
        this.tasks.push(newTask);
        if (!this.activeTaskId) {
            this.activeTaskId = newTask.id;
        }
        this.save();
        this.render();
    }

    toggleComplete(id) {
        const task = this.tasks.find(t => t.id === id);
        if (task) {
            task.completed = !task.completed;
            this.save();
            this.render();
        }
    }

    deleteTask(id) {
        this.tasks = this.tasks.filter(t => t.id !== id);
        if (this.activeTaskId === id) {
            const firstRemaining = this.tasks.find(t => !t.completed);
            this.activeTaskId = firstRemaining ? firstRemaining.id : null;
        }
        this.save();
        this.render();
    }

    setActiveTask(id) {
        this.activeTaskId = id;
        this.render();
    }

    save() {
        localStorage.setItem('zen_tasks', JSON.stringify(this.tasks));
    }

    render() {
        if (!this.tasksListEl) return;

        this.tasksListEl.innerHTML = '';
        let completedCount = 0;

        this.tasks.forEach(task => {
            if (task.completed) completedCount++;

            const li = document.createElement('li');
            li.className = `task-item ${task.completed ? 'completed' : ''} ${task.id === this.activeTaskId ? 'active-selected' : ''}`;
            
            li.innerHTML = `
                <div class="task-left">
                    <div class="task-checkbox" title="${task.completed ? 'Mark incomplete' : 'Mark complete'}">
                        ${task.completed ? '<i class="fa-solid fa-check"></i>' : ''}
                    </div>
                    <span class="task-title">${this.escapeHtml(task.title)}</span>
                </div>
                <div class="task-right">
                    <span class="task-pomo-count" title="Completed / Estimated Pomodoros">
                        <i class="fa-solid fa-clock"></i> ${task.done} / ${task.est}
                    </span>
                    <button class="delete-task-btn" title="Delete Task"><i class="fa-solid fa-trash-can"></i></button>
                </div>
            `;

            // Checkbox click
            const checkbox = li.querySelector('.task-checkbox');
            checkbox.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleComplete(task.id);
            });

            // Delete click
            const deleteBtn = li.querySelector('.delete-task-btn');
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.deleteTask(task.id);
            });

            // Select as active task
            li.addEventListener('click', () => {
                this.setActiveTask(task.id);
            });

            this.tasksListEl.appendChild(li);
        });

        // Update counter badge
        if (this.taskCounterEl) {
            this.taskCounterEl.textContent = `${completedCount} / ${this.tasks.length} Completed`;
        }

        // Update active task header pill
        const activeTask = this.tasks.find(t => t.id === this.activeTaskId);
        if (activeTask && this.activeTaskPill) {
            this.activeTaskPill.classList.remove('hidden');
            this.activeTaskTitle.textContent = activeTask.title;
        } else if (this.activeTaskPill) {
            this.activeTaskPill.classList.add('hidden');
        }
    }

    escapeHtml(str) {
        return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.taskManager = new TaskManager();
});
