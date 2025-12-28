// Mock for rxjs to avoid ESM issues in Jest
class Observable {
  constructor(subscribe) {
    this._subscribe = subscribe;
  }
  subscribe(observer) {
    return this._subscribe(observer);
  }
}

class Subject extends Observable {
  constructor() {
    super((observer) => {
      this.observers.push(observer);
      return () => {
        this.observers = this.observers.filter((o) => o !== observer);
      };
    });
    this.observers = [];
  }
  next(value) {
    this.observers.forEach((observer) => observer.next?.(value));
  }
  error(error) {
    this.observers.forEach((observer) => observer.error?.(error));
  }
  complete() {
    this.observers.forEach((observer) => observer.complete?.());
  }
}

class BehaviorSubject extends Subject {
  constructor(initialValue) {
    super();
    this.value = initialValue;
  }
  next(value) {
    this.value = value;
    super.next(value);
  }
  getValue() {
    return this.value;
  }
}

const of = (...values) => {
  return new Observable((observer) => {
    values.forEach((value) => observer.next(value));
    observer.complete();
  });
};

const from = (input) => {
  return new Observable((observer) => {
    Promise.resolve(input).then((value) => {
      observer.next(value);
      observer.complete();
    });
  });
};

const EMPTY = new Observable((observer) => observer.complete());

module.exports = {
  Observable,
  Subject,
  BehaviorSubject,
  of,
  from,
  EMPTY,
};
